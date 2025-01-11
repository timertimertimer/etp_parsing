# -*- coding: utf-8 -*-
from typing import Iterable

import scrapy
import logging
from bs4 import BeautifulSoup
from icecream import ic
from scrapy import Request, FormRequest
from scrapy.loader import ItemLoader

from ..get_data_from_table import DbConnectCheckLots
from ..items import Lot
from ..config import page_limits, start_from, formdata


class Rutrade24Spider(scrapy.Spider):
    name = 'ruTrade24'
    start_urls = ['https://ru-trade24.ru/query/Filter']

    all_lots = []
    logger = logging.getLogger(__name__)

    def __init__(self):
        super(Rutrade24Spider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self) -> Iterable[Request]:
        yield FormRequest(self.start_urls[0], self.parse, method='POST', formdata=formdata)

    def parse(self, response):
        current_page = self.get_currentPage(response)
        nextPage_url = self.get_next_page(response)
        trade_containers = response.css(".row.row--v-offset.trade-card")

        if len(trade_containers) != 25 and nextPage_url is not None:
            self.logger.warning(
                'Площадка: ru-trade24.ru. ' +
                'Cсылка: %s. ' % response.url +
                'Полученое количество ссылок торгов не равно 25. ' +
                'Полученое количество: \'%s\'.' % len(trade_containers)
            )

        if page_limits['page_start'] <= current_page <= page_limits['page_stop']:
            for trade_container in trade_containers:
                trade_link = 'https://ru-trade24.ru' + trade_container.css('a::attr(href)').get()
                status = trade_container.css('.trade-card__status::text').get()
                if trade_link not in self.previous_lots:
                    yield scrapy.Request(
                        url=trade_link,
                        callback=self.parse_trade,
                        cb_kwargs=dict(status=status)
                    )

        if nextPage_url is not None and current_page <= page_limits['page_stop']:
            formdata['page'] = str(current_page + 1)
            yield FormRequest(self.start_urls[0], method='POST', formdata=formdata, callback=self.parse)

    def get_currentPage(self, response):
        for page in response.css('div.paging a'):
            if page.css('::attr(href)').get() == '#':
                return int(page.css('::text').get())

    def get_next_page(self, response):
        next_href = response.css('.paging__arrow--next::attr(href)').get()

        if next_href is None:
            return None
        else:
            return 'http://ru-trade24.ru/' + next_href

    def parse_trade(self, response, status):
        il = ItemLoader(item=Lot(), response=response)

        il.add_value('data_origin', "http://ru-trade24.ru/")

        il.add_value('trading_id', response.url)
        il.add_value('trading_link', response.url)
        il.add_value('trading_number', response.css('h5::text').get())
        il.add_value('trading_type', self.get_table_value_by(
            'Основные сведения',
            'Форма проведения торгов', response
        ))
        il.add_value('trading_form', self.get_table_value_by(
            'Основные сведения',
            'Форма проведения торгов', response
        ))

        il.add_value('trading_org', [
            self.get_table_value_by(
                'Сведения об организаторе',
                'Фамилия', response
            ),
            self.get_table_value_by(
                'Сведения об организаторе',
                'Имя', response
            ),
            self.get_table_value_by(
                'Сведения об организаторе',
                'Отчество', response
            ),
            self.get_table_value_by(
                'Сведения об организаторе',
                'Полное наименование', response
            )
        ])
        il.add_value('trading_org_inn', self.get_table_value_by(
            'Сведения об организаторе',
            'ИНН', response
        ))
        il.add_value('trading_org_contacts', [
            self.get_table_value_by(
                'Сведения об организаторе',
                'Номер контактного телефона', response
            ),
            self.get_table_value_by(
                'Сведения об организаторе',
                'Адрес электронной почты', response
            )
        ])

        il.add_value('msg_number', self.get_table_value_by(
            'Основные сведения',
            'Номер сообщения «Объявление о проведении торгов» опубликованного в ЕФРСБ', response
        ))
        il.add_value('case_number', self.get_table_value_by(
            'Основные сведения',
            'Номер дела о банкротстве', response
        ))
        il.add_value('debtor_inn', self.get_table_value_by(
            'Сведения о должнике',
            'ИНН', response
        ))
        il.add_value('address', self.get_table_value_by(
            'Основные сведения',
            'Наименование арбитражного суда, рассматривающего дело о банкротстве', response
        ))

        il.add_value('arbit_manager', [
            self.get_table_value_by(
                'Cведения об арбитражном управляющем',
                'Фамилия', response
            ),
            self.get_table_value_by(
                'Cведения об арбитражном управляющем',
                'Имя', response
            ),
            self.get_table_value_by(
                'Cведения об арбитражном управляющем',
                'Отчество', response
            )
        ])
        il.add_value('arbit_manager_inn', self.get_table_value_by(
            'Cведения об арбитражном управляющем',
            'ИНН', response
        ))
        il.add_value('arbit_manager_org', self.get_table_value_by(
            'Cведения об арбитражном управляющем',
            'Наименование СРО', response
        ))

        il.add_value('status', status)
        il.add_value('lot_id', None)
        il.add_value('lot_link', None)
        il.add_value('lot_number', [lot_number.get(
        ) for lot_number in response.css('div#lotlist > h5::text')])
        il.add_value('short_name', None)
        il.add_value('lot_info', self.get_value_by(
            'Сведения об имуществе должника (состав, характеристики, описание, порядок ознакомления с имуществом (предприятием) должника)',
            response))
        il.add_value('property_information', None)

        il.add_value('start_date_requests', self.get_table_value_by(
            'Основные сведения',
            'Дата и время начала представления заявок на участие в торгах', response
        ))
        il.add_value('end_date_requests', self.get_table_value_by(
            'Основные сведения',
            'Дата и время окончания представления заявок на участие в торгах', response
        ))
        il.add_value('start_date_trading', self.get_table_value_by(
            'Основные сведения',
            'Дата и время начала проведения торгов', response
        ))
        il.add_value('end_date_trading', self.get_table_value_by(
            'Основные сведения',
            'Дата и время подведения результатов торгов', response
        ))

        il.add_value('start_price', self.get_value_by(
            'Начальная цена продажи имущества (предприятия) должника, руб.', response))
        il.add_value('step_price', self.get_value_by(
            'Величина повышения начальной цены продажи имущества (предприятия), «шаг аукциона», руб.', response))

        il.add_value('periods', self.get_periodsLots(response))
        il.add_value('files', [
            str(BeautifulSoup(response.text, 'html.parser').select_one('div#doc')),
            self.get_lotFiles(response)
        ])

        return il.load_item()

    def get_table(self, name_table, response):
        parser = BeautifulSoup(response.text, "html.parser")

        for table in parser.select("table.node_view"):
            if table.select_one('th').get_text().strip() == name_table:
                return str(table)

        return None

    def get_table_value_by(self, name_table, name_row, response):
        parser = BeautifulSoup(response.text, "html.parser")

        for table in parser.select("div.collaps-block"):

            if table.select_one('div.collaps-block__title').get_text().strip() == name_table:

                for row in table.select('div.info'):
                    if row.label.get_text().strip() == name_row:
                        return row.div.get_text().strip()

        return None

    def get_value_by(self, name_row, response):
        parser = BeautifulSoup(response.text, "html.parser")
        return [label.findNext("div", {'class': 'info__title'}).get_text().strip() for label in
                parser.find_all("label", text=name_row)]

    def get_lotFiles(self, response):
        parser = BeautifulSoup(response.text, "html.parser")

        result = []
        table = parser.select_one('div#lotlist')

        files_html = None
        for child in table.findChildren():
            if child.name == 'h5' and files_html is not None and files_html == '':
                result.append(files_html)

            if child.name == 'h5':
                files_html = ''
            if child.select_one('div.info__name') is not None and child.select_one(
                    'div.info__name').get_text() == 'Дополнительная информация':
                files_html = str(child.select_one('div.info__title'))
                result.append(files_html)

        if files_html == '':
            result.append(files_html)
        return result

    def get_periodsLots(self, response):
        parser = BeautifulSoup(response.text, "html.parser")

        result = []
        table = parser.select_one('div#lotlist')

        files_html = None
        for child in table.findChildren():
            if child.name == 'h5' and files_html is not None and files_html == '':
                result.append(files_html)

            if child.name == 'h5':
                files_html = ''
            if child.select_one('div.info__name') is not None and child.select_one(
                    'div.info__name').get_text() == 'Периоды снижения цены':
                files_html = str(child.select_one('div.info__title'))
                result.append(files_html)

        if files_html == '':
            result.append(files_html)
        return result
