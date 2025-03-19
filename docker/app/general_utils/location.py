import json
import logging
from pathlib import Path

import pymorphy3
import requests
import re

from natasha import MorphVocab, AddrExtractor
from general_utils.check_inn_email_phone import CheckIfCorrectContactInfo
from general_utils.config import api_key_path, indexes_path
from general_utils.db import DBHelper

logger = logging.getLogger(__name__)

if Path(api_key_path).exists():
    with open(api_key_path) as f:
        api_keys = json.load(f)
else:
    api_keys = dict()

yandex_key = api_keys.get('yandex')
dadata_key = api_keys.get('dadata')

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


class RegionIdentifier:
    storage = None
    regions = None
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
        try:
            addresses = DBHelper.get_addresses_with_regions()
            for address in addresses:
                if address.region:
                    d[address.name] = address.region.name
        except Exception as e:
            logger.error(f'Error in fetching addresses: {e}', exc_info=True)
        return d

    @staticmethod
    def _fetch_regions():
        try:
            return DBHelper.get_region_names()
        except Exception as e:
            logger.error(f'Error in fetching addresses: {e}', exc_info=True)

    @staticmethod
    def _fetch_cities():
        c = {}
        try:
            cities = DBHelper.get_cities_with_regions()
            for city in cities:
                c[city.name] = city.region.name
        except Exception as e:
            logger.error(f'Error in fetching addresses: {e}', exc_info=True)
        return c

    @staticmethod
    def get_yandex_region(address: str):
        api_key = yandex_key
        if not api_key:
            logger.warning('Provide api key for yandex in api_keys.json')
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
                RegionIdentifier._get_region_from_index(address) or
                RegionIdentifier._get_region_from_natasha(address) or
                RegionIdentifier._get_region_from_natasha(parsed_address) or
                RegionIdentifier._get_region_from_text(parsed_address)
                # or Region._get_region_from_api(parsed_address)
        ):
            # Region.storage[address.lower()] = region
            # Region.storage[parsed_address.lower()] = region
            return region
        else:
            logger.warning(f'Not found region for address: "{address}"')

    @staticmethod
    def _get_region_from_storage(address: str):
        if region := RegionIdentifier.get_storage().get(address.lower()):
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
                RegionIdentifier.get_storage().get(address) or
                RegionIdentifier.get_cities().get(address) or
                RegionIdentifier.get_storage().get(normalized_address) or
                RegionIdentifier.get_cities().get(normalized_address)
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
                    return RegionIdentifier.get_cities().get(normalized_address) or RegionIdentifier.get_cities().get(value)
                normalized_address = normalize_phrase(f'{value} {type_}')
                normalized_address2 = normalize_phrase(f'{type_} {value}')
                if not (
                        region :=
                        RegionIdentifier.get_storage().get(normalized_address) or
                        RegionIdentifier.get_storage().get(normalized_address2)
                ):
                    for region in RegionIdentifier.get_regions():
                        if value in region.lower() or normalized_address in region.lower() or normalized_address2 in region.lower():
                            RegionIdentifier.storage[address] = region
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
        if region := RegionIdentifier.get_yandex_region(address):
            logger.info(f'Got from API. Address: "{address}", Region: "{region}"')
            return region


def test_region_from_addresses_table():
    count = 0
    addresses = list(RegionIdentifier.get_storage().items())
    for a, r in list(addresses):
        fr = RegionIdentifier.get_region(a)
        if fr and fr != r:
            RegionIdentifier.get_region(a)
        if fr:
            count += 1
    return addresses, count


if __name__ == '__main__':
    print(RegionIdentifier.get_region('республика северная осетия - алания, ст. луковская моздокского р-на, ул. моздокская дом 124'))
