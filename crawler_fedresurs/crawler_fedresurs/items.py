# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose


class CrawlerFedresursItem(scrapy.Item):
    item_type = scrapy.Field()
    item_type2 = scrapy.Field()
    item_transfer = scrapy.Field()
    links_count = scrapy.Field()
    link = scrapy.Field()
    short_name = scrapy.Field()
    full_name = scrapy.Field()
    address = scrapy.Field()
    phone = scrapy.Field()
    region = scrapy.Field()
    inn = scrapy.Field()
    ogrn = scrapy.Field()
    kpp = scrapy.Field()
    legal_form = scrapy.Field()
    registration_number = scrapy.Field()
    registration_date = scrapy.Field()
    sro = scrapy.Field()
    entry_date = scrapy.Field()
    category = scrapy.Field()
    created_at = scrapy.Field()


class OrgCompanyItem(ItemLoader):
    item_type_out = TakeFirst()
    item_type2_out = TakeFirst()
    item_transfer_out = TakeFirst()
    links_count_out = TakeFirst()
    link_out = TakeFirst()
    short_name_out = TakeFirst()
    full_name_out = TakeFirst()
    address_out = TakeFirst()
    phone_out = TakeFirst()
    region_out = TakeFirst()
    inn_out = TakeFirst()
    ogrn_out = TakeFirst()
    kpp_out = TakeFirst()
    legal_form_out = TakeFirst()
    created_at_out = TakeFirst()


class OrgNameItem(ItemLoader):
    item_type_out = TakeFirst()
    item_type2_out = TakeFirst()
    item_transfer_out = TakeFirst()
    links_count_out = TakeFirst()
    link_out = TakeFirst()
    short_name_out = TakeFirst()
    full_name_out = TakeFirst()
    address_out = TakeFirst()
    phone_out = TakeFirst()
    region_out = TakeFirst()
    inn_out = TakeFirst()
    ogrn_out = TakeFirst()
    created_at_out = TakeFirst()


class ArbitrItem(ItemLoader):
    item_type_out = TakeFirst()
    item_transfer_out = TakeFirst()
    links_count_out = TakeFirst()
    link_out = TakeFirst()
    full_name_out = TakeFirst()
    inn_out = TakeFirst()
    registration_number_out = TakeFirst()
    registration_date_out = TakeFirst()
    sro_out = TakeFirst()
    entry_date_out = TakeFirst()
    created_at_out = TakeFirst()


class DebitorItemLoader(ItemLoader):
    item_type_out = TakeFirst()
    item_transfer_out = TakeFirst()
    links_count_out = TakeFirst()
    link_out = TakeFirst()
    full_name_out = TakeFirst()
    category_out = TakeFirst()
    region_out = TakeFirst()
    address_out = TakeFirst()
    inn_out = TakeFirst()
    ogrn_out = TakeFirst()
    created_at_out = TakeFirst()
