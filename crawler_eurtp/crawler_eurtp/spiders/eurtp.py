import scrapy
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from ..items import Lot
from scrapy.loader import ItemLoader
from ..config import page_limits, start_time
import logging

logger = logging.getLogger(__name__)


class EurtpSpider(scrapy.Spider):
    name = 'eurtp'
    start_urls = ['http://eurtp.ru/']

    # logger = logging.getLogger(__name__)

    def parse(self, response):
        parse_categories = [
            {
                'name_category': 'auctionClose',
                'url_category': f'https://eurtp.ru/Home/AuctionOpen?DateStart={start_time[0]}%2F{start_time[1]}%2F{start_time[2]}%2000%3A00%3A00&page=1'
            },
            {
                'name_category': 'auctionOpen',
                'url_category': f'https://eurtp.ru/Home/AuctionClose?DateStart={start_time[0]}%2F{start_time[1]}%2F{start_time[2]}%2000%3A00%3A00&page=1'
            },
            {
                'name_category': 'competition',
                'url_category': f'https://eurtp.ru/Home/Competition?DateStart={start_time[0]}%2F{start_time[1]}%2F{start_time[2]}%2000%3A00%3A00&page=1'
            },
            {
                'name_category': 'offer',
                'url_category': f'https://eurtp.ru/Home/PublicOffering?DateStart={start_time[0]}%2F{start_time[1]}%2F{start_time[2]}%2000%3A00%3A00&page=1'
            }
        ]

        for category in parse_categories:
            yield scrapy.Request(
                url=category['url_category'],
                cb_kwargs=dict(trading_type=category['name_category']),
                callback=self.collect_links,
            )

        return

    def collect_links(self, response, trading_type):
        links_on_page = [tr.css('td:nth-child(2)>a::attr(href)').get() for tr in
                         response.css('.table-responsive table:nth-child(2) tr')[1:]]
        next_page_url = self.get_nextPageUrl(response)
        current_page = self.get_currentPage(response)

        if page_limits[trading_type]['page_start'] <= current_page and \
                page_limits[trading_type]['page_stop'] >= current_page:
            for link in links_on_page:
                yield scrapy.Request(
                    url='http://eurtp.ru' + link,
                    cb_kwargs=dict(
                        trading_type=trading_type
                    ),
                    callback=self.parse_trades
                )

        if len(links_on_page) == 0 or current_page > page_limits[trading_type]['page_stop']: return
        yield scrapy.Request(
            url=next_page_url,
            cb_kwargs=dict(trading_type=trading_type),
            callback=self.collect_links
        )

    def get_currentPage(self, response):
        for url_param in response.url.split('?')[1].split('&'):
            if url_param.split('=')[0] != 'page': continue
            return int(url_param.split('=')[1])

    def get_nextPageUrl(self, response):
        current_page = self.get_currentPage(response)
        return response.url.replace('page=' + str(current_page), 'page=' + str(current_page + 1))

    def parse_trades(self, response, trading_type):
        lots_on_page = [tr.css('td:nth-child(2)>a::attr(href)').get() for tr in
                        response.css('.table-responsive:first-child table:nth-child(2) tr')[1:]]

        for lot_link in lots_on_page:
            yield scrapy.Request(
                url='http://eurtp.ru' + lot_link,
                cb_kwargs=dict(
                    trading_type=trading_type,
                    trade_response=response
                ),
                callback=self.parse_lot
            )

    def parse_lot(self, response, trading_type, trade_response):
        il = ItemLoader(item=Lot(), response=response)

        ### TRADE

        il.add_value('data_origin', 'http://eurtp.ru/')

        il.add_value('trading_id', trade_response.url)
        il.add_value('trading_link', trade_response.url)
        il.add_value('trading_number', trade_response.url)

        il.add_value('trading_type', trade_response.css('h1::text').get())
        il.add_value('trading_form', trade_response.css('h1::text').get())

        il.add_value('trading_org', self.get_table_value(
            'Контактное лицо',
            'ФИО',
            trade_response
        ))
        il.add_value('trading_org_contacts', [
            self.get_table_value(
                'Контактное лицо',
                'Телефон',
                trade_response
            ),
            self.get_table_value(
                'Контактное лицо',
                'Адрес электронной почты',
                trade_response
            )
        ])

        il.add_value('case_number', self.get_table_value(
            'Информация о должнике',
            'Номер дела о банкротстве',
            trade_response
        ))
        il.add_value('debtor_inn', [
            self.get_table_value(
                'Данные должника - физического лица',
                'ИНН',
                trade_response
            ),
            self.get_table_value(
                'Данные должника - юридического лица',
                'ИНН',
                trade_response
            ),
            self.get_table_value(
                'Данные должника - ИП',
                'ИНН',
                trade_response
            )
        ])

        il.add_value('arbit_manager', [
            self.get_table_value(
                'Информация об арбитражном управляющем',
                'Фамилия',
                trade_response
            ),
            self.get_table_value(
                'Информация об арбитражном управляющем',
                'Имя',
                trade_response
            ),
            self.get_table_value(
                'Информация об арбитражном управляющем',
                'Отчество',
                trade_response
            )
        ])
        il.add_value('arbit_manager_inn', self.get_table_value(
            'Информация об арбитражном управляющем',
            'ИНН',
            trade_response
        ))
        il.add_value('arbit_manager_org', self.get_table_value(
            'Информация об арбитражном управляющем',
            'Наименование СРО',
            trade_response
        ))

        ### LOT

        il.add_value('lot_id', response.url)
        il.add_value('lot_link', response.url)
        il.add_value('lot_number', self.get_table_value(
            'Общая информация',
            'Номер',
            response
        ))

        il.add_value('short_name', self.get_table_value(
            'Общая информация',
            'Наименование',
            response
        ))
        il.add_value('lot_info', self.get_table_value(
            'Общая информация',
            'Сведения об имуществе, его составе и характеристиках, описание',
            response
        ))
        il.add_value('property_information', self.get_table_value(
            'Общая информация',
            'Порядок ознакомления с имуществом',
            response
        ))

        ### MULTIPLLE

        il.add_value('start_date_requests', [
            self.get_table_value(
                'Датирование',
                'Дата начала приема заявок на участие в открытом аукционе',
                trade_response
            ),
            self.get_table_value(
                'Датирование',
                'Дата начала приема заявок на участие в конкурсе',
                trade_response
            )
        ])
        il.add_value('end_date_requests', [
            self.get_table_value(
                'Датирование',
                'Дата окончания приема заявок на участие в открытом аукционе',
                trade_response
            ),
            self.get_table_value(
                'Датирование',
                'Дата окончания приема заявок на участие в конкурсе',
                trade_response
            )
        ])
        il.add_value('start_date_trading', [
            self.get_table_value(
                'Датирование',
                'Дата проведения открытого аукциона',
                trade_response
            ),
            self.get_table_value(
                'Датирование',
                'Дата проведения конкурса',
                trade_response
            )
        ])

        il.add_value('start_price', self.get_table_value(
            'Общая информация',
            'Начальная цена',
            response
        ))
        il.add_value('step_price', [
            self.get_table_value(
                'Общая информация',
                'Единицы шага',
                response
            ),
            self.get_table_value(
                'Общая информация',
                'Введите значение шага',
                response
            ),
            self.get_table_value(
                'Общая информация',
                'Значение шага',
                response
            )
        ])

        il.add_value('periods', self.get_periods(response))
        il.add_value('files', [
            self.get_files(trade_response),
            self.get_files(response)
        ])

        return il.load_item()

    def get_table_value(self, name_table, name_row, response):
        parser = BeautifulSoup(response.text, "html.parser")

        for table_cont in parser.select('.etp-block'):
            if table_cont.h2 is None: continue
            if table_cont.h2.get_text().strip() != name_table: continue
            for row in table_cont.select('tr'):
                try:
                    if row.select('td')[0].get_text().strip() == row.select('td')[1].get_text().strip(): return \
                        row.select('td')[1].get_text().strip()
                    if row.select('td')[0].get_text().strip() != name_row: continue

                    return row.select('td')[1].get_text().strip()
                except Exception as e:
                   
                    return None

        return None

    def get_periods(self, response):
        parser = BeautifulSoup(response.text, "html.parser")

        periods = []

        for table_cont in parser.select('.etp-block'):
            if table_cont.h2 is None: continue
            if table_cont.h2.get_text().strip() != 'Общая информация': continue
            for row in table_cont.select('tr'):
                if not row.select('td')[0].get_text().strip().startswith('Промежуток'): continue
                if len(row.select('td')) < 2: continue
                periods.append(row.select('td')[1].get_text().strip())

        return periods

    def get_files(self, response):
        parser = BeautifulSoup(response.text, "html.parser")
        return parser.select_one('.etp-main-content>.row:last-child table:last-child')
