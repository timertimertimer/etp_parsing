# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose
import json


def check_trading_type(string: str = None):
    """
    Check what type of trade
    :return:
    """
    offer = ['Публичное предложение',
             'Закрытое публичное предложение']
    auction = ['Аукцион с открытой формой представления цены',
               'Аукцион с закрытой формой представления цены',
               'Закрытый аукцион с открытой формой представления цены',
               'Закрытый аукцион с закрытой формой представления цены']
    competition = ['Конкурс с открытой формой представления цены',
                   'Конкурс с закрытой формой представления цены',
                   'Закрытый конкурс с открытой формой представления цены',
                   'Закрытый конкурс с закрытой формой представления цены']

    if str(string).strip() in auction:
        return 'auction'
    elif str(string).strip() in offer:
        return 'offer'
    elif (str(string).strip() in competition):
        return 'competition'
    else:
        return None


def check_trading_form(string: str = None):
    """
    Check what form
    :param form:str
    :return: trading form: open/closed
    """
    open_form = ['Аукцион с открытой формой представления цены',
                 'Аукцион с закрытой формой представления цены',
                 'Конкурс с открытой формой представления цены',
                 'Конкурс с закрытой формой представления цены',
                 'Публичное предложение']
    close_form = ['Закрытый аукцион с открытой формой представления цены',
                  'Закрытый аукцион с закрытой формой представления цены',
                  'Закрытый конкурс с открытой формой представления цены',
                  'Закрытый конкурс с закрытой формой представления цены',
                  'Закрытое публичное предложение']

    if str(string).strip() in open_form:
        return 'open'
    elif str(string).strip() in close_form:
        return 'close'
    else:
        return None


def check_status(status_lot: str = None):
    """
    Check status
    :param status: str
    :return: staus of trade
    """
    active = ('Прием заявок',)
    pending = ('Торги объявлены',)
    ended = ('Прием заявок завершен', 'Идут торги', 'Подведение итогов',
             'Торги завершены', 'Торги не состоялись', 'Торги отменены')
    try:
        if str(status_lot).strip() in active:
            return 'active'
        elif str(status_lot).strip() in pending:
            return 'pending'
        elif str(status_lot).strip() in ended:
            return 'ended'
    except:
        return None


def to_str(value):
    data = str(value)
    return data


def to_json(value):
    try:
        data = json.dumps(value, indent=4, ensure_ascii=False).encode('utf-8')
        return data
    except:
        data = json.dumps(value, indent=4, ensure_ascii=True).encode('utf-8')
        return data


def from_lst_dict_to_str(value):
    data = list(map(lambda x: str(x).replace(',', '\n'), value))
    return '\n'.join(data)


class SistematorgItem(scrapy.Item):
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


class SistematorgTradeItem(scrapy.Item):
    data_origin = scrapy.Field(output_processor=TakeFirst())
    trading_id = scrapy.Field(output_processor=TakeFirst())
    trading_link = scrapy.Field(output_processor=TakeFirst())
    trading_number = scrapy.Field(output_processor=TakeFirst())
    trading_type = scrapy.Field(output_processor=TakeFirst())
    trading_form = scrapy.Field(output_processor=TakeFirst())
    trading_status = scrapy.Field(output_processor=TakeFirst())
    last_name_org = scrapy.Field(output_processor=TakeFirst())
    first_name_org = scrapy.Field(output_processor=TakeFirst())
    middle_name_org = scrapy.Field(output_processor=TakeFirst())
    full_name = scrapy.Field(output_processor=TakeFirst())
    company_name = scrapy.Field(output_processor=TakeFirst())
    inn_org = scrapy.Field(output_processor=TakeFirst())
    email_org = scrapy.Field(output_processor=TakeFirst())
    phone_org = scrapy.Field(output_processor=TakeFirst())
    trading_contacts = scrapy.Field(output_processor=MapCompose())
    msg_number = scrapy.Field(output_processor=TakeFirst())
    case_number = scrapy.Field(output_processor=TakeFirst())
    debtor_inn = scrapy.Field(output_processor=TakeFirst())
    arbit_manager = scrapy.Field(output_processor=TakeFirst())
    arbit_manager_inn = scrapy.Field(output_processor=TakeFirst())
    arbit_manager_org = scrapy.Field(output_processor=TakeFirst())
    start_date_requests = scrapy.Field(output_processor=TakeFirst())
    end_date_requests = scrapy.Field(output_processor=TakeFirst())
    start_date_trading = scrapy.Field(output_processor=TakeFirst())
    end_date_trading = scrapy.Field(output_processor=TakeFirst())
    original_name = scrapy.Field(output_processor=TakeFirst())
    general = scrapy.Field(output_processor=MapCompose())


class SistematorgItemLoader(ItemLoader):
    data_origin_out = TakeFirst()
    trading_id_out = TakeFirst()
    trading_link_out = TakeFirst()
    trading_number_out = TakeFirst()
    trading_type_out = Compose(TakeFirst(), check_trading_type)
    trading_form_out = Compose(TakeFirst(), check_trading_form)
    status_out = Compose(TakeFirst(), check_status)
    msg_number_out = TakeFirst()
    case_number_out = TakeFirst()
    debtor_inn_out = TakeFirst()
    trading_org_out = TakeFirst()
    trading_org_inn_out = TakeFirst()
    trading_org_contacts_out = Compose(TakeFirst(), to_json)
    arbit_manager_out = TakeFirst()
    arbit_manager_inn_out = TakeFirst()
    arbit_manager_org_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    lot_id_out = TakeFirst()
    lot_link_out = TakeFirst()
    lot_number_out = TakeFirst()
    short_name_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    lot_info_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
    property_information_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', '\''), str)
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
