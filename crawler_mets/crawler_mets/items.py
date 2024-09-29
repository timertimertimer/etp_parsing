import json

import scrapy
from itemloaders.processors import TakeFirst, Compose
from scrapy.loader import ItemLoader


def check_status(status: str = None):
    """
    Check status
    :param status: str
    :return: status of trade
    """
    active = ('Торги в стадии приема заявок', 'Прием заявок',)
    pending = ('Объявленые торги', 'Объявленные торги')
    ended = ('Прием заявок завершен', 'Проведение аукциона', 'Торги завершены', 'Торги отменены',
             'Торги приостановлены', 'Торги по лоту отменены', 'Торги по лоту приостановлены')
    try:
        if status in active:
            return 'active'
        elif status in pending:
            return 'pending'
        elif status in ended:
            return 'ended'
        else:
            return None
    except:
        return None


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


class CrawlerMetsItem(scrapy.Item):
    data_origin = scrapy.Field()
    trading_id = scrapy.Field()
    trading_link = scrapy.Field()
    trading_number = scrapy.Field()
    trading_type = scrapy.Field()
    trading_form = scrapy.Field()
    trading_org = scrapy.Field()
    trading_org_inn = scrapy.Field()
    trading_org_contacts = scrapy.Field()
    msg_number = scrapy.Field()
    case_number = scrapy.Field()
    debtor_inn = scrapy.Field()
    arbit_manager = scrapy.Field()
    arbit_manager_inn = scrapy.Field()
    arbit_manager_org = scrapy.Field()
    status = scrapy.Field()
    lot_id = scrapy.Field()
    lot_link = scrapy.Field()
    lot_number = scrapy.Field()
    short_name = scrapy.Field()
    lot_info = scrapy.Field()
    property_information = scrapy.Field()
    start_date_requests = scrapy.Field()
    end_date_requests = scrapy.Field()
    start_date_trading = scrapy.Field()
    end_date_trading = scrapy.Field()
    start_price = scrapy.Field()
    step_price = scrapy.Field()
    periods = scrapy.Field()
    files = scrapy.Field()
    file_lots = scrapy.Field()
    created_at = scrapy.Field()


class MetsItemLoader(ItemLoader):
    data_origin_out = TakeFirst()
    trading_id_out = TakeFirst()
    trading_link_out = TakeFirst()
    trading_number_out = TakeFirst()
    trading_type_out = TakeFirst()
    trading_form_out = TakeFirst()
    status_out = Compose(TakeFirst(), check_status)
    msg_number_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    case_number_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    debtor_inn_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    trading_org_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    trading_org_inn_out = TakeFirst()
    trading_org_contacts_out = Compose(TakeFirst(), to_json)
    arbit_manager_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    arbit_manager_inn_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    arbit_manager_org_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    lot_id_out = TakeFirst()
    lot_link_out = TakeFirst()
    lot_number_out = TakeFirst()
    short_name_out = TakeFirst()
    lot_info_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    property_information_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    start_date_requests_out = TakeFirst()
    end_date_requests_out = TakeFirst()
    start_date_trading_out = TakeFirst()
    end_date_trading_out = TakeFirst()
    start_price_out = TakeFirst()
    step_price_out = TakeFirst()
    periods_out = Compose(to_json)
    files_out = Compose(TakeFirst(), to_json)
    created_at_out = TakeFirst()
