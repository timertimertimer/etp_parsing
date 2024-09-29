# -*- coding: utf-8 -*-
import scrapy
import logging
from bs4 import BeautifulSoup
from scrapy.loader import ItemLoader
from crawler_eltorg.items import Lot
from crawler_eltorg.config import page_limits, start_time


class EltorgSpider(scrapy.Spider):
    name = 'eltorg'
    start_urls = [
        f'http://el-torg.com/bankrot/trade_list.php?trade_number=&debtor_info=&arbitr_info=&app_start_from={start_time}&app_start_to=&app_end_from=&app_end_to=&trade_type=%D0%9B%D1%8E%D0%B1%D0%BE%D0%B9&trade_state=%D0%9B%D1%8E%D0%B1%D0%BE%D0%B9&pagenum=1'
    ]

    logger = logging.getLogger(__name__)

    def parse(self, response):
        current_page = self.get_current_page(response)
        next_page_url = self.get_next_page_url(response)

        if response.css("table.data>tbody>tr::text").get() is None: return

        if page_limits['page_start'] <= current_page <= page_limits['page_stop']:
            lot_links = [row.css('td:nth-child(3)>a::attr(href)').get() for row in response.css("table.data>tbody>tr")]
            for lot_link in lot_links:
                yield scrapy.Request(
                        url=lot_link, 
                        callback=self.parse_lot
                    )
        if current_page > page_limits['page_stop']:
            return
        yield scrapy.Request(
                url=next_page_url, 
                callback=self.parse
            )        

    def get_current_page(self, response):
        for param_url in response.url.split('?')[1].split('&'):
            if param_url.split('=')[0] == 'pagenum': return int(param_url.split('=')[1])
        
        self.logger.warning(
            'Площадка: el-torg. ' +
            'Не получен номер текущей страницы.' +
            'Полученое значение url: %s' % response.url
        )
        return None

    def get_next_page_url(self, response):
        current_page = self.get_current_page(response)
        next_page = current_page + 1

        return self.start_urls[0][:-1] + str(next_page)

    def parse_lot(self, response):
        il = ItemLoader(item=Lot(), response=response)

        il.add_value('data_origin', "http://el-torg.com/")

        il.add_css('trading_id', 'a.op_link::attr(href)')
        il.add_css('trading_link', 'a.op_link::attr(href)')
        il.add_css('trading_number', 'h1.node_header::text')
        il.add_value('trading_type', self.get_table_value_by(
                                            'Информация о ходе торгов',
                                            'Тип торгов', response
                                        ))
        il.add_value('trading_form', self.get_table_value_by(
                                            'Информация о ходе торгов',
                                            'Тип торгов', response
                                        ))

        il.add_value('trading_org', self.get_table_value_by(
                                            'Контактное лицо организатора торгов',
                                            'ФИО',response
                                        ))
        il.add_value('trading_org_inn', 'null')
        il.add_value('trading_org_contacts', [
            self.get_table_value_by(
                'Контактное лицо организатора торгов',
                'Телефон', response
            ),
            self.get_table_value_by(
                'Контактное лицо организатора торгов',
                'E-mail', response
            )
        ])

        il.add_value('msg_number', self.get_table_value_by(
                                            'Информация о проведении торгов',
                                            'Номер объявления о проведении торгов на fedresurs.ru', response
                                        ))
        il.add_value('case_number', self.get_table_value_by(
                                            'Информация о должнике',
                                            'Номер дела о банкротстве', response
                                        ))
        il.add_value('debtor_inn', self.get_table_value_by(
                                            'Информация о должнике',
                                            'ИНН', response
                                        ))
        
        il.add_value('arbit_manager', [
            self.get_table_value_by(
                'Информация об арбитражном управляющем',
                'Фамилия', response
            ),
            self.get_table_value_by(
                'Информация об арбитражном управляющем',
                'Имя', response
            ),
            self.get_table_value_by(
                'Информация об арбитражном управляющем',
                'Отчество', response
            )
        ])
        il.add_value('arbit_manager_inn', self.get_table_value_by(
                                            'Информация об арбитражном управляющем',
                                            'ИНН', response
                                        ))
        il.add_value('arbit_manager_org', self.get_table_value_by(
                                            'Информация об арбитражном управляющем',
                                            'Наименование СРО', response
                                        ))

        il.add_value('status', self.get_value_by('Статус торгов', response))
        il.add_value('lot_id', response.url)
        il.add_value('lot_link', response.url)
        il.add_value('lot_number', self.get_value_by('Номер лота', response))
        il.add_value('short_name', self.get_value_by('Наименование имущества', response))
        il.add_value('lot_info', self.get_value_by('Cведения об имуществе (предприятии) должника, выставляемом на торги, его составе, характеристиках, описание', response))
        il.add_value('property_information', self.get_table_value_by(
                                            'Информация о проведении торгов', 
                                            'Порядок ознакомления с имуществом', response
                                        ))
        
        il.add_value('start_date_requests', self.get_table_value_by(
                                            'Информация о ходе торгов',
                                            'Дата начала представления заявок на участие', response
                                        ))
        il.add_value('end_date_requests', self.get_table_value_by(
                                            'Информация о ходе торгов',
                                            'Дата окончания представления заявок на участие', response
                                        ))
        il.add_value('start_date_trading', self.get_table_value_by(
                                            'Информация о ходе торгов',
                                            'Дата проведения', response
                                        ))
        il.add_value('end_date_trading', self.get_table_value_by(
                                            'Информация о ходе торгов',
                                            'Дата окончания представления заявок на участие', response
                                        ))
        
        il.add_value('start_price', self.get_value_by('Начальная цена', response)) 
        il.add_value('step_price', self.get_value_by('Шаг аукциона', response))

        il.add_css('periods', 'table.inner.discount_int')
        il.add_css('files', 'table.node_view td.file_container')

        return il.load_item()

    def get_table_value_by(self, name_table, name_row, response):
        parser = BeautifulSoup(response.text, "html.parser")

        is_need_table = False

        for tr in parser.find_all("tr"):
            if tr.find("th", {"colspan" : "2"}) is not None and tr.find("th", {"colspan" : "2"}).get_text().strip() == name_table:
                is_need_table = True
                continue

            if not is_need_table:
                continue

            if tr.td is not None and tr.td.get_text().strip() == name_row:
                return tr.select("td")[-1].get_text().strip()
            
            if is_need_table and tr.find("th", {"colspan" : "2"}) is not None:
                return

    def get_value_by(self, name_row, response):
        parser = BeautifulSoup(response.text, "html.parser")
        return [td.findNext("td").get_text().strip() for td in parser.find_all("td", text=name_row)]