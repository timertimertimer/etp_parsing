from datetime import datetime

import scrapy
from scrapy import Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose, Identity

from app.utils.datetime_helper import DateTimeHelper


class EtpItem(scrapy.Item):
    data_origin = scrapy.Field()
    property_type = Field()
    trading_id = scrapy.Field()
    trading_link = scrapy.Field()
    trading_number = scrapy.Field()
    trading_type = scrapy.Field()  # auction/offer/competition
    trading_form = scrapy.Field()  # open/closed
    trading_org = scrapy.Field()
    trading_org_inn = scrapy.Field()
    trading_org_contacts = scrapy.Field()
    msg_number = scrapy.Field()  # № сообщения ЕФРСБ
    case_number = scrapy.Field()  # № судебного дела
    debtor_inn = scrapy.Field()
    address = scrapy.Field()
    arbit_manager = scrapy.Field()
    arbit_manager_inn = scrapy.Field()
    arbit_manager_org = scrapy.Field()
    status = scrapy.Field()  # статус торгов (активные/ ожидаются/ завершенные)
    lot_id = scrapy.Field()
    lot_link = scrapy.Field()
    lot_number = scrapy.Field()
    short_name = (
        scrapy.Field()
    )  # Краткие сведения об имуществе (предприятии) должника (наименование лота)
    lot_info = scrapy.Field()  # Cведения об имуществе (предприятии) должника, выставляемом на торги, его составе, характеристиках, описание
    categories = scrapy.Field()
    property_information = (
        scrapy.Field()
    )  # Порядок ознакомления с имуществом (предприятием) должника
    start_date_requests = scrapy.Field()
    end_date_requests = scrapy.Field()
    start_date_trading = scrapy.Field()
    end_date_trading = scrapy.Field()
    start_price = scrapy.Field()
    step_price = scrapy.Field()
    periods = scrapy.Field()
    files = scrapy.Field()
    application_fee = scrapy.Field()  # Обеспечение заявки/Вознаграждение оператора
    performance_security_fee = scrapy.Field()  # Обеспечение обязательств по договору
    execution_time = (
        scrapy.Field()
    )  # Информация о сроках исполнения контракта и источниках финансирования
    subject_info = (
        scrapy.Field()
    )  # Информация об объекте закупки/Информация о товаре, работе, услуге
    sme = scrapy.Field()  # Только для малого и среднего предпринимательства да/нет/неизвестно ГАЛОЧКА В ФИЛЬТРЕ

def format_and_set_moscow_tz(datetime_instance: datetime):
    if not datetime_instance:
        return None
    return DateTimeHelper.format_datetime(datetime_instance.astimezone(DateTimeHelper.moscow_tz))

def format_periods(periods):
    date_keys = ["start_date_requests", "end_date_requests", "end_date_trading"]
    for period in periods:
        for key in date_keys:
            if key in period and period[key]:
                period[key] = format_and_set_moscow_tz(period[key])
    return periods


class EtpItemLoader(ItemLoader):
    data_origin_out = TakeFirst()
    property_type_out = TakeFirst()
    trading_id_out = TakeFirst()
    trading_link_out = TakeFirst()
    trading_number_out = TakeFirst()
    trading_type_out = TakeFirst()
    trading_form_out = TakeFirst()
    status_out = TakeFirst()
    msg_number_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', "'"), str)
    case_number_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', "'"), str)
    debtor_inn_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', "'"), str)
    address_out = TakeFirst()
    trading_org_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', "'"), str)
    trading_org_inn_out = TakeFirst()
    trading_org_contacts_out = TakeFirst()
    arbit_manager_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', "'"), str)
    arbit_manager_inn_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', "'"), str
    )
    arbit_manager_org_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', "'"), str
    )
    lot_id_out = TakeFirst()
    lot_link_out = TakeFirst()
    lot_number_out = TakeFirst()
    short_name_out = TakeFirst()
    lot_info_out = Compose(TakeFirst(), lambda x: x.strip().replace('"', "'"), str)
    categories_out = TakeFirst()
    property_information_out = Compose(
        TakeFirst(), lambda x: x.strip().replace('"', "'"), str
    )
    start_date_requests_out = Compose(TakeFirst(), format_and_set_moscow_tz)
    end_date_requests_out = Compose(TakeFirst(), format_and_set_moscow_tz)
    start_date_trading_out = Compose(TakeFirst(), format_and_set_moscow_tz)
    end_date_trading_out = Compose(TakeFirst(), format_and_set_moscow_tz)
    start_price_out = TakeFirst()
    step_price_out = TakeFirst()
    periods_out = Compose(format_periods)
    files_out = TakeFirst()
    bid_security_out = TakeFirst()
    performance_security_out = TakeFirst()
    operators_fee_out = TakeFirst()
    subject_info_out = TakeFirst()
    sme_out = TakeFirst()
