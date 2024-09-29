import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose
import re
import json

from .utils.manage_spider import return_itself


def check_trading_form(string):
    """
    Check what form
    :param string:str
    :return: trading form: open/closed
    """
    open_form = ['Публичное предложение продавца',
                 'Открытый аукцион с открытой формой подачи ценовых предложений',
                 'Открытый аукцион с закрытой формой подачи ценовых предложений',
                 'Открытый конкурс',
                 'Аукцион продавца',
                 'Аукцион с закрытой формой подачи предложений о цене', 'open']
    close_form = ['Закрытый аукцион с открытой формой подачи ценовых предложений',
                  'Закрытый аукцион с закрытой формой подачи ценовых предложений',
                  'Закрытый конкурс']
    match1 = ''.join(filter(lambda x: re.findall(
        string, x, flags=re.IGNORECASE), open_form))
    match2 = ''.join(filter(lambda x: re.findall(
        string, x, flags=re.IGNORECASE), close_form))

    if match1:
        return 'open'
    elif match2:
        # open is True on this case on fabricant
        return 'open'
    else:
        return 'open'


def check_status(status: str = None):
    """
    Check status
    :param status: str
    :return: staus of trade
    """
    active = ('Этап приема заявок', 'Проводятся торги')
    pending = ('Ожидание этапа приема заявок',)
    try:
        if status in active:
            return 'active'
        elif status in pending:
            return 'pending'
        else:
            return 'ended'
    except:
        return None


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


def from_lst_dict_to_str(value):
    data = list(map(lambda x: str(x).replace(',', '\n'), value))
    return '\n'.join(data)


class CrawlerSberbankItem(scrapy.Item):
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


class TradingSberbankItem(scrapy.Item):
    data_origin = scrapy.Field(output_processor=TakeFirst())
    trading_id = scrapy.Field(output_processor=TakeFirst())
    trading_link = scrapy.Field(output_processor=TakeFirst())
    trading_number = scrapy.Field(output_processor=TakeFirst())
    trading_type = scrapy.Field(output_processor=TakeFirst())
    trading_form = scrapy.Field(output_processor=TakeFirst())
    trading_org = scrapy.Field(output_processor=TakeFirst())
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
    files_trade = scrapy.Field(output_processor=MapCompose())


class SberbankItemLoader(ItemLoader):
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
    short_name_out = Compose(TakeFirst(), return_itself)
    lot_info_out = Compose(
        TakeFirst(), return_itself)
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
