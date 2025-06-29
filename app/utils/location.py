import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import json
import pymorphy3
import requests
import re
from natasha import MorphVocab, AddrExtractor

from .contacts import Contacts
from .config import env, indexes_path
from .logger import logger
from app.db.db_helper import DBHelper
from app.db.models import Region

punctuation = r"""!"#$%&'()*+,./:;<=>?@[\]^_`{|}~"""

with open(indexes_path, encoding="utf-8") as f:
    indexes = json.load(f)

morph_vocab = MorphVocab()
extractor = AddrExtractor(morph_vocab)
morph = pymorphy3.MorphAnalyzer()
region_keywords = {
    "область",
    "край",
    "округ",
    "республика",
    "город",
    "автономный округ",
}
use_api_services = {"yandex": False, "dadata": True}


def parse_address(address: str):
    if any(["суд" in address.lower().split(), "суда" in address.lower().split()]):
        pattern = r"(?i)(?:арбитражн\w*\s+)?суд\w*\s+(.+)"
        try:
            address = re.search(pattern, address).group(1)
        except AttributeError:
            pass
    elif address.startswith("АС"):
        pattern = r"АС\s*(.+)"
        try:
            address = re.search(pattern, address).group(1)
        except AttributeError:
            pass

    address = re.sub(r"\d+", "", address)
    replacements = [
        " от ",
        " по ",
        " №",
        "д.",
        "ком.",
        "корп.",
        "ст.",
        "помещ.",
        "офис",
        "кв.",
        "комн",
        "комн.",
        "квартира",
        "обл.",
        "с.п.",
        "м.р-н",
        "тер.",
        "п.",
        "с.",
        "дер.",
        "пос.",
        "поселок",
        "посёлок",
        "посёлок",
        "вн.тер.г.",
        "г.о.",
        "пр-кт",
        " дом ",
    ]
    replacements2 = {
        "г.": "город",
        "ул.": "улица",
        "гор.": "город",
        "обл.": "область",
        "респ.": "республика",
    }
    address = address.split(" и ")[0]
    for replacement in replacements2:
        address = address.replace(replacement, replacements2[replacement] + " ")
    for replacement in replacements:
        address = address.replace(replacement, "")
    address = "".join(char for char in address if char not in punctuation)
    address = address.strip()
    parsed_address = []
    replacements = {"обл": "область", "г": "город", "респ": "республика"}
    for word in address.split():
        if replacement := replacements.get(word):
            word.replace(word, replacement)
        if len(word) > 1:
            parsed_address.append(word)
    return " ".join(parsed_address)


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
                normalized_words[i - 1] = previous_word.inflect(
                    {gender, case, number}
                ).word
    normalized_phrase = " ".join(normalized_words)
    return normalized_phrase


def get_index(address: str):
    match = re.search(r"\b\d{6}\b", address)
    if match:
        return match.group()
    return None


class RegionIdentifier:
    storage = None
    regions = None
    cities = None
    oktmos = None

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

    @classmethod
    def get_oktmos(cls):
        if cls.oktmos is None:
            cls.oktmos = cls._fetch_oktmos()
        return cls.oktmos

    @staticmethod
    def _fetch_addresses():
        d = {}
        try:
            addresses = DBHelper.get_addresses_with_regions()
            for address in addresses:
                if address.region:
                    d[address.name] = address.region.name
        except Exception as e:
            logger.warning(f"Error in fetching addresses: {e}")
        return d

    @staticmethod
    def _fetch_regions():
        try:
            return [region.name for region in DBHelper.get_all(Region)]
        except Exception as e:
            logger.warning(f"Error in fetching addresses: {e}")
        return None

    @staticmethod
    def _fetch_cities():
        c = {}
        try:
            cities = DBHelper.get_cities_with_regions()
            for city in cities:
                c[city.name] = city.region.name
        except Exception as e:
            logger.warning(f"Error in fetching addresses: {e}")
        return c

    @staticmethod
    def _fetch_oktmos():
        o = {}
        try:
            return {region.oktmo: region.name for region in DBHelper.get_all(Region)}
        except Exception as e:
            logger.warning(f"Error in fetching addresses: {e}")
        return o

    @staticmethod
    def get_yandex_region(address: str):
        if not env.yandex_api_key:
            logger.warning("No api key for Yandex API")
            return None
        params = {
            "apikey": env.yandex_api_key,
            "geocode": address,
            "lang": "ru_RU",
            "format": "json",
        }
        response = requests.get("https://geocode-maps.yandex.ru/1.x", params=params)
        data = response.json()
        if not data.get("response"):
            logger.warning(f'Error while parsing address: "{address}" - {data}')
            return None
        feature_member = data["response"]["GeoObjectCollection"]["featureMember"]
        if not feature_member:
            region = None
        else:
            keys = [
                "GeoObject",
                "metaDataProperty",
                "GeocoderMetaData",
                "AddressDetails",
                "Country",
                "AdministrativeArea",
                "AdministrativeAreaName",
            ]
            region = feature_member[0]
            for key in keys:
                if key == "AdministrativeArea":
                    if region.get("CountryName") != "Россия":
                        region = None
                        break
                region = region.get(key)
                if not region:
                    break
        return region

    @staticmethod
    def get_dadata_region(address: str):
        if not env.env.dadata_api_token or not env.dadata_api_secret:
            logger.warning("No api key for Dadata API")
            return None
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Token {env.dadata_api_token}",
            "X-Secret": env.dadata_api_secret,
        }
        response = requests.post(
            "https://cleaner.dadata.ru/api/v1/clean/address",
            headers=headers,
            json=[address],
        )
        data = response.json()
        if not data:
            pass
        region = data[0]["region"]
        region_type_full = data[0]["region_type_full"]
        region_with_type = data[0]["region_with_type"]
        oktmo = data[0]["oktmo"]
        region_type = data[0]["region_type"]
        postal_code = data[0]["postal_code"]
        if region_type_full == "город":
            return RegionIdentifier.get_cities()[region.lower()]
        elif postal_code:
            return RegionIdentifier._get_region_from_index(postal_code)
        elif oktmo:
            return (
                RegionIdentifier.get_oktmos().get(int(oktmo))
                or RegionIdentifier.get_oktmos().get(int(oktmo[:3] + "0" * 5))
                or RegionIdentifier.get_oktmos().get(int(oktmo[:2] + "0" * 6))
            )
        elif region:
            return region
        return None

    @staticmethod
    def get_region(address: str):
        address = Contacts.check_address(address)
        if not address:
            return None
        parsed_address = parse_address(address)

        region = None
        if (
            region :=
            # RegionIdentifier._get_region_from_storage(address) or
            RegionIdentifier._get_region_from_index(address)
            or RegionIdentifier._get_region_from_natasha(address)
            or RegionIdentifier._get_region_from_natasha(parsed_address)
            or RegionIdentifier._get_region_from_text(parsed_address)
            or RegionIdentifier._get_region_from_api(address)
        ):
            # RegionIdentifier.storage[address.lower()] = region
            # RegionIdentifier.storage[parsed_address.lower()] = region
            return region
        else:
            logger.warning(f'Not found region for address: "{address}"')
        return None

    @staticmethod
    def _get_region_from_storage(address: str | None):
        if not address:
            return None
        if region := RegionIdentifier.get_storage().get(address.lower()):
            logger.info(f'Got from storage. Address: "{address}", Region: "{region}"')
            return region
        return None

    @staticmethod
    def _get_region_from_index(address: str | None):
        if not address:
            return None
        index = get_index(address)
        if index:
            if region := indexes.get(index[:3]):
                logger.info(
                    f'Got from indexes. Address: "{address}", Region: "{region}"'
                )
                return region
            logger.warning(f'Index "{index}" not found in indexes. Address: {address}')
        return None

    @staticmethod
    def _get_region_from_text(address: str):
        normalized_address = normalize_phrase(address)
        return (
            RegionIdentifier.get_storage().get(address)
            or RegionIdentifier.get_cities().get(address)
            or RegionIdentifier.get_storage().get(normalized_address)
            or RegionIdentifier.get_cities().get(normalized_address)
        )

    @staticmethod
    def _get_region_from_natasha(address: str):
        region = None
        matches = list(extractor(address))
        for match in matches:
            type_ = match.fact.type
            value = match.fact.value
            if type_ in region_keywords:
                if type_ == "город":
                    normalized_address = normalize_phrase(value)
                    return RegionIdentifier.get_cities().get(
                        normalized_address
                    ) or RegionIdentifier.get_cities().get(value)
                normalized_address = normalize_phrase(f"{value} {type_}")
                normalized_address2 = normalize_phrase(f"{type_} {value}")
                if not (
                    region := RegionIdentifier.get_storage().get(normalized_address)
                    or RegionIdentifier.get_storage().get(normalized_address2)
                ):
                    for region in RegionIdentifier.get_regions():
                        if (
                            value in region.lower()
                            or normalized_address in region.lower()
                            or normalized_address2 in region.lower()
                        ):
                            RegionIdentifier.storage[address] = region
                            logger.info(
                                f'Got with natasha. Address: "{address}", Region: "{region}"'
                            )
                            break
                    else:
                        return None
                return region
            elif type_ not in [
                "индекс",
                "село",
                "дом",
                "квартира",
                "страна",
                None,
                "улица",
                "офис",
                "строение",
                "корпус",
                "площадь",
                "проспект",
                "переулок",
                "бульвар",
                "шоссе",
                "линия",
                "набережная",
                "проезд",
                "тупик",
                "просек",
            ]:
                return None
        else:
            return None

    @staticmethod
    def _get_region_from_api(address: str | None):
        if not address or len(address) < 3:
            return None
        if use_api_services["yandex"] and (
            region := RegionIdentifier.get_yandex_region(address)
        ):
            logger.info(
                f'Got from Yandex API. Address: "{address}", Region: "{region}"'
            )
            return region
        if use_api_services["dadata"] and (
            region := RegionIdentifier.get_dadata_region(address)
        ):
            logger.info(
                f'Got from Dadata API. Address: "{address}", Region: "{region}"'
            )
            return region
        return None


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


if __name__ == "__main__":
    from sqlalchemy import select
    from app.db.models import Address, Region

    with DBHelper.transaction_scope(commit=False) as session:
        addresses = (
            session.execute(select(Address).where(Address.region_id.is_(None)))
            .scalars()
            .all()
        )
        for address in addresses:
            region_name = RegionIdentifier.get_region(address.name)
            region = session.execute(
                select(Region).where(Region.name.like(f"%{region_name}%"))
            ).scalar()
            if region:
                address.region_id = region.id
                session.commit()
            else:
                logger.warning(f"No region found for address: {address.name}")
