# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import json
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Compose

import scrapy


def to_json(value):
    try:
        data = json.dumps(value, indent=1, ensure_ascii=False).encode('utf-8')
        return data
    except:
        data = json.dumps(value, indent=1, ensure_ascii=True).encode('utf-8')
        return data


class CrawlerMsgFedresursItem(scrapy.Item):
    message_link = scrapy.Field()
    message_type = scrapy.Field()
    message_number = scrapy.Field()
    publish_date = scrapy.Field()
    debtor_inn = scrapy.Field()
    case_number = scrapy.Field()
    # Объявление о проведении торгов
    # Сообщение о результатах торгов
    # Сообщение об отмене сообщения об объявлении торгов или сообщения о результатах торгов
    lots = scrapy.Field()
    files = scrapy.Field()
    # Объявление о проведении торгов
    debtor_name = scrapy.Field()
    debtor_address = scrapy.Field()
    # Сообщение об отмене сообщения об объявлении торгов или сообщения о результатах торгов
    canceled_message = scrapy.Field()
    # Сообщение о результатах торгов
    announced_message = scrapy.Field()
    # Сообщение об изменении объявления о проведении торгов
    modified_message = scrapy.Field()
    created_at = scrapy.Field()


class MsgFedresursItemLoader(ItemLoader):
    message_link_out = TakeFirst()
    message_type_out = TakeFirst()
    message_number_out = TakeFirst()
    publish_date_out = TakeFirst()
    debtor_inn_out = TakeFirst()
    case_number_out = TakeFirst()
    # Объявление о проведении торгов
    # Сообщение о результатах торгов
    # Сообщение об отмене сообщения об объявлении торгов или сообщения о результатах торгов
    lots_out = Compose(to_json)
    files_out = Compose(to_json)
    # Объявление о проведении торгов
    debtor_name_out = TakeFirst()
    debtor_address_out = TakeFirst()
    # Сообщение об отмене сообщения об объявлении торгов или сообщения о результатах торгов
    canceled_message_out = TakeFirst()
    # Сообщение о результатах торгов
    announced_message_out = TakeFirst()
    # Сообщение об изменении объявления о проведении торгов
    modified_message_out = TakeFirst()
    created_at_out = TakeFirst()
