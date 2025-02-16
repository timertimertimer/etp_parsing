import copy
import json
import logging
import random
import time
from pprint import pprint

import pymorphy3
import requests
import re

from mysql.connector import MySQLConnection
from natasha import MorphVocab, AddrExtractor

from general_utils import read_db_config
from general_utils.check_inn_email_phone import CheckIfCorrectContactInfo
from general_utils.config import api_key_path, indexes_path

logger = logging.getLogger(__name__)

with open(api_key_path) as f:
    api_keys = json.load(f)

yandex_key = api_keys['yandex']
dadata_key = api_keys['dadata']

punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""

with open(indexes_path, encoding='utf-8') as f:
    indexes = json.load(f)

morph_vocab = MorphVocab()
extractor = AddrExtractor(morph_vocab)
morph = pymorphy3.MorphAnalyzer()
region_keywords = {"область", "край", "округ", "республика", "город", 'автономный округ'}


def parse_address(address: str):
    if any([
        'суд' in address.lower().split(),
        'суда' in address.lower().split()
    ]):
        pattern = r"(?i)(?:арбитражн\w*\s+)?суд\w*\s+(.+)"
        try:
            address = re.search(pattern, address).group(1)
        except AttributeError as e:
            pass
    elif address.startswith('АС'):
        pattern = r"АС\s*(.+)"
        try:
            address = re.search(pattern, address).group(1)
        except AttributeError as e:
            pass

    address = re.sub(r'\d+', '', address)
    replacements = [
        ' от ', ' по ', ' №', 'д.', 'ком.', 'корп.', 'ст.', 'помещ.', 'офис', 'кв.', 'комн', 'комн.',
        'квартира', 'обл.', 'с.п.', 'м.р-н', 'тер.', 'п.', 'с.', 'дер.', 'пос.', 'поселок', 'посёлок', 'посёлок',
        'вн.тер.г.', 'г.о.', 'пр-кт', ' дом '
    ]
    replacements2 = {
        'г.': 'город',
        'ул.': 'улица',
        'гор.': 'город',
        'обл.': 'область',
        'респ.': 'республика',
    }
    address = address.split(' и ')[0]
    for replacement in replacements2:
        address = address.replace(replacement, replacements2[replacement] + ' ')
    for replacement in replacements:
        address = address.replace(replacement, '')
    address = ''.join(char for char in address if char not in punctuation)
    address = address.strip()
    parsed_address = []
    replacements = {
        'обл': 'область',
        'г': 'город',
        'респ': 'республика'
    }
    for word in address.split():
        if replacement := replacements.get(word):
            word.replace(word, replacement)
        if len(word) > 1:
            parsed_address.append(word)
    return ' '.join(parsed_address)


def normalize_phrase(phrase: str):
    words = phrase.split()
    normalized_words = [morph.parse(word)[0].normal_form for word in words]
    for i, word in enumerate(normalized_words):
        if word in region_keywords and i > 0:
            # Предыдущее слово должно быть прилагательным
            previous_word = morph.parse(normalized_words[i - 1])[0]
            if "ADJF" in previous_word.tag:  # Если слово — прилагательное
                # Согласовываем прилагательное с существительным (род, число, падеж)
                gender = morph.parse(word)[0].tag.gender  # Род существительного
                case = morph.parse(word)[0].tag.case  # Падеж существительного
                number = morph.parse(word)[0].tag.number  # Число существительного
                # Склоняем прилагательное
                normalized_words[i - 1] = previous_word.inflect({gender, case, number}).word
    normalized_phrase = ' '.join(normalized_words)
    return normalized_phrase


def get_index(address: str):
    match = re.search(r"\b\d{6}\b", address)
    if match:
        return match.group()


class Region:
    storage = None
    regions = None
    lower_regions = None
    cities = None

    @classmethod
    def get_storage(cls):
        if cls.storage is None:
            cls.storage = cls._fetch_addresses()
        return cls.storage

    @classmethod
    def get_regions(cls):
        if cls.regions is None:
            cls.regions = cls._fetch_regions()
        return cls.regions

    @classmethod
    def get_cities(cls):
        if cls.cities is None:
            cls.cities = cls._fetch_cities()
        return cls.cities

    @staticmethod
    def _fetch_addresses():
        d = {}
        db_config = read_db_config()
        try:
            with MySQLConnection(**db_config) as conn:
                with conn.cursor() as curr:
                    curr.execute("SELECT address, region FROM addresses")
                    for key, value in curr.fetchall():
                        d[key] = value
        except Exception as e:
            logger.error(f'Error in fetching addresses: {e}', exc_info=True)
        return d

    @staticmethod
    def _fetch_regions():
        r = []
        db_config = read_db_config()
        try:
            with MySQLConnection(**db_config) as conn:
                with conn.cursor() as curr:
                    curr.execute("SELECT distinct region FROM addresses")
                    for value in curr.fetchall():
                        r.append(value[0])
        except Exception as e:
            logger.error(f'Error in fetching addresses: {e}', exc_info=True)
        return r

    @staticmethod
    def _fetch_cities():
        c = {}
        db_config = read_db_config()
        try:
            with MySQLConnection(**db_config) as conn:
                with conn.cursor() as curr:
                    curr.execute("SELECT city, region FROM cities")
                    for key, value in curr.fetchall():
                        c[key] = value
        except Exception as e:
            logger.error(f'Error in fetching addresses: {e}', exc_info=True)
        return c

    @staticmethod
    def get_yandex_region(address: str):
        api_key = yandex_key
        params = {
            'apikey': api_key,
            'geocode': address,
            'lang': 'ru_RU',
            'format': 'json'
        }
        response = requests.get('https://geocode-maps.yandex.ru/1.x', params=params)
        data = response.json()
        if not data.get('response'):
            logger.warning(f'Error while parsing address: "{address}" - {data}')
            return
        feature_member = data['response']['GeoObjectCollection']['featureMember']
        if not feature_member:
            region = None
        else:
            keys = ['GeoObject', 'metaDataProperty', 'GeocoderMetaData', 'AddressDetails', 'Country',
                    'AdministrativeArea',
                    'AdministrativeAreaName']
            region = feature_member[0]
            for key in keys:
                if key == 'AdministrativeArea':
                    if region.get('CountryName') != 'Россия':
                        region = None
                        break
                region = region.get(key)
                if not region:
                    break
        return region

    @staticmethod
    def get_region(address: str):
        address = CheckIfCorrectContactInfo.check_address(address)
        if not address:
            return
        parsed_address = parse_address(address)

        if (
                region :=
                # Region._get_region_from_storage(address) or
                Region._get_region_from_index(address) or
                Region._get_region_from_natasha(address) or
                Region._get_region_from_natasha(parsed_address) or
                Region._get_region_from_text(parsed_address)
                # or Region._get_region_from_api(parsed_address)
        ):
            # Region.storage[address.lower()] = region
            # Region.storage[parsed_address.lower()] = region
            return region
        else:
            logger.warning(f'No region found for address: "{address}"')

    @staticmethod
    def _get_region_from_storage(address: str):
        if region := Region.get_storage().get(address.lower()):
            logger.info(f'Got from storage. Address: "{address}", Region: "{region}"')
            return region

    @staticmethod
    def _get_region_from_index(address: str):
        index = get_index(address)
        if index:
            if region := indexes.get(index[:3]):
                logger.info(f'Got from indexes. Address: "{address}", Region: "{region}"')
                return region
            logger.warning(f'Index "{index}" not found in indexes. Address: {address}')

    @staticmethod
    def _get_region_from_text(address: str):
        normalized_address = normalize_phrase(address)
        if not (
                region :=
                Region.get_storage().get(address) or
                Region.get_cities().get(address) or
                Region.get_storage().get(normalized_address) or
                Region.get_cities().get(normalized_address)
        ):
            # cities = Region.get_cities()
            # address_lower = address.lower()
            #
            # for city, region in cities.items():
            #     if (
            #             re.search(r'\b' + re.escape(city) + r'\b', address_lower) or
            #             re.search(r'\b' + re.escape(city) + r'\b', normalized_address)
            #     ):
            #         logger.info(f'Found city "{city}" in address "{address}", region: "{region}"')
            #         return region
            pass
        return region

    @staticmethod
    def _get_region_from_natasha(address: str):
        matches = list(extractor(address))
        for match in matches:
            type_ = match.fact.type
            value = match.fact.value
            if type_ in region_keywords:
                if type_ == 'город':
                    normalized_address = normalize_phrase(value)
                    return Region.get_cities().get(normalized_address) or Region.get_cities().get(value)
                normalized_address = normalize_phrase(f'{value} {type_}')
                normalized_address2 = normalize_phrase(f'{type_} {value}')
                if not (
                        region :=
                        Region.get_storage().get(normalized_address) or
                        Region.get_storage().get(normalized_address2)
                ):
                    for region in Region.get_regions():
                        if value in region.lower() or normalized_address in region.lower() or normalized_address2 in region.lower():
                            Region.storage[address] = region
                            logger.info(f'Got with natasha. Address: "{address}", Region: "{region}"')
                            break
                    else:
                        return
                return region
            elif type_ not in [
                'индекс', 'село', 'дом', 'квартира', 'страна', None, 'улица', 'офис', 'строение', 'корпус', 'площадь',
                'проспект', 'переулок', 'бульвар', 'шоссе', 'линия', 'набережная', 'проезд', 'тупик', 'просек',
            ]:
                pass
        else:
            pass

    @staticmethod
    def _get_region_from_api(address: str):
        if region := Region.get_yandex_region(address):
            logger.info(f'Got from API. Address: "{address}", Region: "{region}"')
            return region

    @staticmethod
    def save_new_regions_to_db():
        db_config = read_db_config()
        storage = Region.storage or {}
        try:
            with MySQLConnection(**db_config) as conn:
                with conn.cursor() as curr:
                    curr.execute("SELECT address FROM addresses")
                    existing_addresses = {row[0].lower() for row in curr.fetchall()}
                    new_entries = {address: region for address, region in storage.items() if
                                   address.lower() not in existing_addresses and region}
                    if not new_entries:
                        logger.info("Нет новых записей для сохранения.")
                        return
                    insert_query = """
                        INSERT INTO addresses (address, region) 
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE address = address
                    """
                    curr.executemany(insert_query, list(new_entries.items()))
                    conn.commit()
                    logger.info(f"Успешно добавлено {len(new_entries)} новых записей.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении новых записей: {e}", exc_info=True)


def test_region_from_addresses_table():
    count = 0
    addresses = list(Region.get_storage().items())
    for a, r in list(addresses):
        fr = Region.get_region(a)
        if fr and fr != r:
            Region.get_region(a)
        if fr:
            count += 1
    return addresses, count


def test_region_from_all_addresses():
    from general_utils.db import DBHelper
    count = 0
    addresses = DBHelper().get_all_addresses()
    for address in addresses:
        fr = Region.get_region(address)
        if fr:
            count += 1
    return addresses, count


if __name__ == '__main__':
    start = time.time()
    addresses, count = test_region_from_all_addresses()
    end = time.time()
    print(f'executed in {end - start} seconds')
    print(f'found {count} regions of {len(addresses)} addresses')
    print(f'{(count / len(addresses) * 100):.2f}%')
    Region.save_new_regions_to_db()
