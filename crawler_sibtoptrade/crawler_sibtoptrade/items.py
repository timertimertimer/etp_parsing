# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose, MapCompose
import re
import json


def check_trading_type(string_):
    """
    Check what type of trade
    :param string_:str
    :return:
    """
    offer = ['Публичное предложение']
    auction = ['Открытый аукцион',
               'Закрытый аукцион']
    competition = ['Конкурс']
#    pattern = r'(\D{4}$)'
#    match = ''.join(re.findall(pattern, str(code).strip()))
    string_ = (''.join(string_)).strip()
    if string_ in auction:
        return 'auction'
    elif string_ in offer:
        return 'offer'
    elif string_ in competition:
        return 'competition'
    else:
        return None


def check_trading_form(string_):
    """
    Check what form
    :param string_:str
    :return: trading form: open/closed
    """
    open_form = ['Открытый аукцион',
                 'Конкурс',
                 'Публичное предложение']
    close_form = ['Закрытый аукцион']
#    pattern = r'(\D{4}$)'
#    match = ''.join(re.findall(pattern, str(code).strip()))
    string_ = (''.join(string_)).strip()
    if string_ in open_form:
        return 'open'
    elif string_ in close_form:
        return 'close'
    else:
        return None


def check_status(status: str = None):
    """
    Check status
    :param status: str
    :return: staus of trade
    """
    active = ('идёт приём заявок', 'идет прием заявок')
    pending = ('объявлены',)
    ended = ('приём заявок завершен', 'в стадии проведения', 'подводятся итоги',
             'торги завершены', 'торги отменены', 'прием заявок завершен', 'идёт приём заявок (приостановлены)')
    try:
        if status in active:
            return 'active'
        elif status in pending:
            return 'pending'
        elif status in ended:
            return 'ended'
    except:
        return None


def get_lot_number(value):
    pattern = r'^Лот.?\W\d{1,}\:?'
    match = ''.join(re.findall(pattern, (''.join(value)).strip()))
    match = ''.join(re.findall(r'\d+', match))
    try:
        if match:
            return match
        else:
            return '1'
    except:
        return '1'


def to_str(value: dict) -> dict:
    data = value
    return data


def to_json(value):
    try:
        data = json.dumps(value, indent=1, ensure_ascii=False).encode('utf-8')
        return data
    except:
        data = json.dumps(value, indent=1, ensure_ascii=True).encode('utf-8')
        return data


def cut_lot_number(value):
    pattern = r'^Лот.?\W\d{1,}\:?'
    match = ''.join(re.findall(pattern, (''.join(value)).strip()))
    if match:
        value = value.replace(match, '').strip().replace('"', '\'')
        return value
    else:
        return value.strip().replace('"', '\'')
    pass


def from_lst_dict_to_str(value):
    data = list(map(lambda x: str(x).replace(',', '\n'), value))
    return '\n'.join(data)


class SibtopItem(scrapy.Item):
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


class SibtopItemLoader(ItemLoader):
    data_origin_out = TakeFirst()
    trading_id_out = TakeFirst()
    trading_link_out = TakeFirst()
    trading_number_out = TakeFirst()
    trading_type_out = Compose(TakeFirst(), check_trading_type)
    trading_form_out = Compose(TakeFirst(), check_trading_form)
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
    lot_number_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
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
    start_price_out = TakeFirst()
    step_price_out = TakeFirst()
    periods_out = Compose(to_json)
    files_out = Compose(TakeFirst(), to_json)
    created_at_out = TakeFirst()


class DownlodItem(scrapy.Item):
    lot = scrapy.Field(output_processor=MapCompose())
    general = scrapy.Field(output_processor=MapCompose())
