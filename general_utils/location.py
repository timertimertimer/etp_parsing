import json
import logging
import random
import requests
import re

from mysql.connector import MySQLConnection

from general_utils import read_db_config
from general_utils.config import yandex_api_keys_path

logger = logging.getLogger(__name__)

with open(yandex_api_keys_path) as f:
    api_keys = json.load(f)

punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""


class Region:
    storage = None

    @classmethod
    def get_addresses(cls):
        if cls.storage is None:
            cls.storage = cls._fetch_addresses()
        return cls.storage

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
    def get_region(address: str):
        if not address:
            return
        region = Region.get_addresses().get(address.lower())
        if region:
            return region
        initial_address = address
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
        replacements = {
            ' от ': ' ',
            ' по ': ' ',
            ' №': '',
            'г.': '',
            'ул.': '',
            'д.': '',
            'ком.': '',
            'корп.': '',
            'ст.': '',
        }
        address = address.split(' и ')[0]
        for key, value in replacements.items():
            address = address.replace(key, value)
        address = ''.join(char for char in address if char not in punctuation)
        address = address.strip()
        parsed_address = []
        for word in address.split():
            if len(word) > 2:
                parsed_address.append(word)
        address = ' '.join(parsed_address)
        api_key, proxy = random.choice(list(api_keys.items()))
        params = {
            'apikey': api_key,
            'geocode': address,
            'lang': 'ru_RU',
            'format': 'json'
        }
        response = requests.get(
            'https://geocode-maps.yandex.ru/1.x', params=params, proxies={'http': proxy} if proxy else None
        )
        data = response.json()
        if not data.get('response'):
            logger.error(f'Error while parsing address: "{initial_address}" - {data}')
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
        logger.info(f'Address: "{initial_address}", Parsed address: "{address}", Region: "{region}"')
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
                                   address.lower() not in existing_addresses}
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
    print(Region.get_region('Арбитражного суда Ханты-Мансийского автономного округа - Югры'))
