import json
import logging
import random
from pprint import pprint

import requests
import re

from mysql.connector import MySQLConnection

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
        ' от ', ' по ', ' №', 'г.', 'ул.', 'д.', 'ком.', 'корп.', 'ст.', 'помещ.', 'офис', 'кв.', 'комн', 'комн.',
        'квартира', 'обл.', 'с.п.', 'м.р-н', 'тер.', 'п.', 'с.', 'дер.', 'пос.', 'поселок', 'посёлок', 'посёлок',
        'вн.тер.г.', 'г.о.', 'пр-кт', ' дом '
    ]
    address = address.split(' и ')[0]
    for replacement in replacements:
        address = address.replace(replacement, '')
    address = ''.join(char for char in address if char not in punctuation)
    address = address.strip()
    parsed_address = []
    for word in address.split():
        if len(word) > 2:
            parsed_address.append(word)
    return ' '.join(parsed_address)


def get_index(address: str):
    match = re.search(r"\b\d{6}\b", address)
    if match:
        return match.group()


class Region:
    storage = None
    regions = None

    @classmethod
    def get_addresses(cls):
        if cls.storage is None:
            cls.storage = cls._fetch_addresses()
        return cls.storage

    @classmethod
    def get_regions(cls):
        if cls.regions is None:
            cls.regions = cls._fetch_regions()
        return cls.regions

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

        region = Region.get_addresses().get(address.lower())
        if region:
            logger.info(f'Found in storage. Address: "{address}", Region: "{region}"')
            return region

        index = get_index(address)
        if index:
            region = indexes.get(index[:3])
            if region:
                logger.info(f'Found in indexes. Address: "{address}", Region: "{region}"')
                return region
            logger.warning(f'Index "{index}" not found in indexes.')

        initial_address = address
        parsed_address = parse_address(address)
        region = Region.get_addresses().get(parsed_address.lower())
        if region:
            logger.info(f'Found in storage. Address: "{parsed_address}", Region: "{region}"')
            return region
        region = Region.get_yandex_region(parsed_address)
        logger.info(f'Address: "{initial_address}", Parsed address: "{parsed_address}", Region: "{region}"')
        Region.storage[initial_address.lower()] = region
        Region.storage[address.lower()] = region
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
                    insert_query = "INSERT INTO addresses (address, region) VALUES (%s, %s)"
                    curr.executemany(insert_query, list(new_entries.items()))
                    conn.commit()
                    logger.info(f"Успешно добавлено {len(new_entries)} новых записей.")
        except Exception as e:
            logger.error(f"Ошибка при сохранении новых записей: {e}", exc_info=True)


if __name__ == '__main__':
    print(Region.get_region('298650, Республика Крым, г Ялта, ул Стахановская, 18, 2, 7'))
