import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose, MapCompose
import json


def to_str(value: dict) -> dict:
    data = value
    return data


def to_json(value: list):
    try:
        data = json.dumps(value, indent=1, ensure_ascii=False).encode('utf-8')
        return data
    except:
        data = json.dumps(value, indent=1, ensure_ascii=True).encode('utf-8')
        return data


def from_lst_dict_to_str(value):
    data = list(map(lambda x: str(x).replace(',', '\n'), value))
    return '\n'.join(data)


class CrawlerTorgigovItem(scrapy.Item):
    data_origin = scrapy.Field()
    trading_id = scrapy.Field()
    trading_link = scrapy.Field()
    trading_number = scrapy.Field()
    trading_type = scrapy.Field()
    trading_form = scrapy.Field()
    trading_org = scrapy.Field()
    trading_org_contacts = scrapy.Field()
    status = scrapy.Field()
    category = scrapy.Field()
    index = scrapy.Field()
    address = scrapy.Field()
    detailed_address = scrapy.Field()
    encumbrance = scrapy.Field()
    description_encumbrance = scrapy.Field()
    lot_number = scrapy.Field()
    short_name = scrapy.Field()
    lot_info = scrapy.Field()
    property_information = scrapy.Field()
    start_date_requests = scrapy.Field()
    end_date_requests = scrapy.Field()
    start_date_trading = scrapy.Field()
    end_date_trading = scrapy.Field()
    quantity = scrapy.Field()
    unit = scrapy.Field()
    deposit = scrapy.Field()
    min_price = scrapy.Field()
    start_price = scrapy.Field()
    step_price = scrapy.Field()
    periods = scrapy.Field()
    files = scrapy.Field()
    created_at = scrapy.Field()

class CrawlerTorgigovItemLoader(ItemLoader):
    data_origin_out = TakeFirst()
    trading_id_out = TakeFirst()
    trading_link_out = TakeFirst()
    trading_number_out = TakeFirst()
    trading_type_out = TakeFirst()
    trading_form_out = TakeFirst()
    trading_org_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    trading_org_contacts_out = Compose(TakeFirst(), to_json)
    status_out = TakeFirst()
    category_out = Compose(TakeFirst(), to_json)
    index_out = TakeFirst()
    address_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    detailed_address_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    encumbrance_out = TakeFirst()
    description_encumbrance_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    lot_number_out = TakeFirst()
    short_name_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    lot_info_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    property_information_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    start_date_requests_out = TakeFirst()
    end_date_requests_out = TakeFirst()
    start_date_trading_out = TakeFirst()
    end_date_trading_out = TakeFirst()
    quantity_out = TakeFirst()
    unit_out = TakeFirst()
    deposit_out = TakeFirst()
    min_price_out = TakeFirst()
    start_price_out = TakeFirst()
    step_price_out = TakeFirst()
    periods_out = Compose(to_json)
    files_out = Compose(TakeFirst(), to_json)
    created_at_out = TakeFirst()

