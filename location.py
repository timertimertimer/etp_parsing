import json
import random
import requests
import re
from pathlib import Path

with open(Path(__file__).parent / 'yandex_api_keys.json') as f:
    api_keys = json.load(f)

punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""


def get_region(address: str):
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

    address = ''.join(char for char in address if char not in punctuation)
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
    feature_member = data['response']['GeoObjectCollection']['featureMember']
    if not feature_member:
        region = None
    else:
        keys = ['GeoObject', 'metaDataProperty', 'GeocoderMetaData', 'AddressDetails', 'Country', 'AdministrativeArea',
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
    print(f'Адрес: {address}, Регион: {region}')
    return region


if __name__ == '__main__':
    print(get_region('Арбитражный суда Магаданской области'))
