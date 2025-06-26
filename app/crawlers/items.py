import scrapy
from scrapy import Field
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, Compose, Identity


class EtpItem(scrapy.Item):
    data_origin = scrapy.Field()
    auction_property = Field()
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
    address = scrapy.Field()
    arbit_manager = scrapy.Field()
    arbit_manager_inn = scrapy.Field()
    arbit_manager_org = scrapy.Field()
    status = scrapy.Field()
    lot_id = scrapy.Field()
    lot_link = scrapy.Field()
    lot_number = scrapy.Field()
    short_name = scrapy.Field()
    lot_info = scrapy.Field()
    categories = scrapy.Field()
    property_information = scrapy.Field()
    start_date_requests = scrapy.Field()
    end_date_requests = scrapy.Field()
    start_date_trading = scrapy.Field()
    end_date_trading = scrapy.Field()
    start_price = scrapy.Field()
    step_price = scrapy.Field()
    periods = scrapy.Field()
    files = scrapy.Field()


class EtpItemLoader(ItemLoader):
    data_origin_out = TakeFirst()
    auction_property_out = TakeFirst()
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
    start_date_requests_out = TakeFirst()
    end_date_requests_out = TakeFirst()
    start_date_trading_out = TakeFirst()
    end_date_trading_out = TakeFirst()
    start_price_out = TakeFirst()
    step_price_out = TakeFirst()
    periods_out = Identity()
    files_out = TakeFirst()
