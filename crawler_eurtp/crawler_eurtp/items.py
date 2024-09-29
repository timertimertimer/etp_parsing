# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from itemloaders.processors import TakeFirst

class Lot(scrapy.Item):

    data_origin = scrapy.Field(output_processor=TakeFirst())

    trading_id = scrapy.Field(output_processor=TakeFirst())
    trading_link = scrapy.Field(output_processor=TakeFirst())
    trading_number = scrapy.Field(output_processor=TakeFirst())
    
    trading_type = scrapy.Field(output_processor=TakeFirst())
    trading_form = scrapy.Field(output_processor=TakeFirst())

    trading_org = scrapy.Field(output_processor=TakeFirst())
    trading_org_inn = scrapy.Field()
    trading_org_contacts = scrapy.Field()

    msg_number = scrapy.Field()
    case_number = scrapy.Field(output_processor=TakeFirst())
    debtor_inn = scrapy.Field()
    
    arbit_manager = scrapy.Field()
    arbit_manager_inn = scrapy.Field(output_processor=TakeFirst())
    arbit_manager_org = scrapy.Field(output_processor=TakeFirst())
    
    status = scrapy.Field()

    lot_id = scrapy.Field(output_processor=TakeFirst())
    lot_link = scrapy.Field(output_processor=TakeFirst())
    lot_number = scrapy.Field(output_processor=TakeFirst())
    short_name = scrapy.Field(output_processor=TakeFirst())
    lot_info = scrapy.Field(output_processor=TakeFirst())
    property_information = scrapy.Field(output_processor=TakeFirst())

    start_date_requests = scrapy.Field()
    end_date_requests = scrapy.Field()
    start_date_trading = scrapy.Field()
    end_date_trading = scrapy.Field()

    start_price = scrapy.Field(output_processor=TakeFirst())
    step_price = scrapy.Field()

    periods = scrapy.Field()
    files = scrapy.Field()