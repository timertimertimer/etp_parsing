import logging
import re
from itertools import chain

from scrapy import Request, FormRequest
from scrapy.spiders import Spider

from general_utils import CrawlerBankruptItem, CrawlerBankruptItemLoader
from ..manage_spiders.app import Combo
from ..utils.config import _data_origin, _serp_link, _lot_link, _doc_link, path_absolute, path_relative, url_file, \
    tables
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.query_parameters import query_param
from ..utils.working_with_time import return_parse_date
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)
TABLE = tables['table_etp_profit_ru']


class EtpProfitRuSpider(Spider):
    name = 'etp_profit_ru'
    allowed_domains = ['etp-profit.ru']
    data_origin = _data_origin['etp_profit_ru']
    lot_link = _lot_link['etp_profit_ru']
    serp_link = _serp_link['etp_profit_ru']
    doc_link = _doc_link['etp_profit_ru']
    full_path = path_absolute['etp_profit_ru']
    relative_path = path_relative['etp_profit_ru']
    main_url = url_file['etp_profit_ru']
    start_url = [serp_link]

    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }

    def __init__(self, *args, **kwargs):
        super(EtpProfitRuSpider, self).__init__(*args, **kwargs)
        self.url = UrlConfig()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot(TABLE)

    def start_requests(self):
        url = self.url.unquote_url(self.start_url[0])
        yield Request(url, self.make_query_search)

    def make_query_search(self, response):
        """ request for searching lots in special period """
        yield FormRequest(response.url, callback=self.parse_serp, method='GET',
                          formdata=query_param, dont_filter=True, cb_kwargs={'current_page': 1})

    def parse_serp(self, response, current_page):
        combo = Combo(response_=response)
        if links := combo.serp.get_links_to_trade():
            for link in links:
                url = self.url.unquote_url(self.start_url[0].replace('/index.html', '').strip())
                url = self.url.url_join(url, link)
                if prev := self.previous_lots:
                    if url not in prev:
                        yield Request(url, callback=self.parse_trade_page, dont_filter=True)
                else:
                    yield Request(url, callback=self.parse_trade_page, dont_filter=True)
        # pagination
        next_page = combo.serp.get_one_next_link()
        if next_page:
            current_page += 1
            url = response.urljoin(next_page)
            yield Request(url, self.parse_serp, dont_filter=True, cb_kwargs={'current_page': current_page})

    # def start_requests(self):
    #     url = 'https://xn-----6kcbaifbn4di5abenic8aq7kvd6a.xn--p1ai/trade/view/purchase/general.html?id=101758388'
    #     yield Request(url, self.parse_trade_page)

    def parse_trade_page(self, response):
        """ parse trading page and get same info for the all types """
        combo = Combo(response_=response)
        trading_form = combo.serp.get_trading_form()
        if trading_form:
            trading_type = combo.serp.get_trading_type()
            transfer = CrawlerBankruptItem()
            transfer['data_origin'] = self.data_origin
            id_trade = combo.serp.get_trading_id(url=response.url)
            transfer['trading_id'] = id_trade
            transfer['trading_link'] = response.url
            transfer['trading_number'] = combo.serp.get_trading_number()
            transfer['trading_type'] = trading_type
            transfer['trading_form'] = trading_form
            transfer['trading_org'] = combo.serp.get_trading_org()
            transfer['trading_org_inn'] = None
            transfer['trading_org_contacts'] = combo.serp.get_org_contacts()
            transfer['msg_number'] = combo.serp.get_msg_number()
            transfer['case_number'] = combo.serp.get_case_number()
            transfer['debtor_inn'] = combo.serp.get_debtor_inn()
            transfer['address'], transfer['region'] = combo.serp.get_address() or (None, None)
            transfer['arbit_manager'] = combo.serp.get_arbitr_name()
            transfer['arbit_manager_inn'] = None
            transfer['arbit_manager_org'] = combo.serp.get_arb_org()
            if trading_type == 'auction' or trading_type == 'competition':
                transfer['start_date_requests'] = combo.auc.start_date_request_auc()
                transfer['end_date_requests'] = combo.auc.end_date_request_auc()
                transfer['start_date_trading'] = combo.auc.start_date_trading_auc()
                transfer['end_date_trading'] = combo.auc.end_date_trading_auc()
            try:
                yield Request(self.doc_link + f'{id_trade}&&id={id_trade}',
                              callback=self.parse_doc_page, dont_filter=True,
                              cb_kwargs={'transfer': transfer, '_id': id_trade,
                                         'trading_type': trading_type})
            except Exception as e:
                logger.error(f'{response.url} :: ERROR DURING REQUEST TO DOC PAGE {self.doc_link} {e}')

    def parse_doc_page(self, response, transfer, _id, trading_type):
        """ parse page with docs """
        callback_func = None
        combo = Combo(response_=response)
        main_url = self.main_url
        current_page = 1
        general_docs = None
        general_docs = combo.doc.general_docs(full_path=self.full_path, relative_path=self.relative_path,
                                              main_url=main_url, _id=_id)
        local_lot_link = self.url.unquote_url(self.lot_link) + f'{_id}&page={current_page}'
        # if local_lot_link == 'https://торговая-площадка-вэтп.рф/etp/trade/inner-view-lots.html?perspective=inline&id=102041647&page=1':
        if trading_type == 'auction':
            callback_func = self.parse_auction_lot
        if trading_type == 'offer':
            callback_func = self.parse_offer_lot
        if trading_type == 'competition':
            callback_func = self.parse_competition_lot
        if callback_func:
            yield Request(local_lot_link, callback=callback_func, dont_filter=True,
                          cb_kwargs={'general_docs': general_docs, 'current_page': current_page,
                                     'transfer': transfer, 'link': local_lot_link})

    def parse_auction_lot(self, response, transfer, general_docs, current_page, link):
        """ parse page with lots """
        combo = Combo(response_=response)
        for table in combo.auc.get_all_lot_tables():
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', transfer['data_origin'])
            loader.add_value('trading_id', transfer['trading_id'])
            loader.add_value('trading_link', transfer['trading_link'])
            loader.add_value('trading_number', transfer['trading_number'])
            loader.add_value('trading_type', transfer['trading_type'])
            loader.add_value('trading_form', transfer['trading_form'])
            loader.add_value('trading_org', transfer['trading_org'])
            loader.add_value('trading_org_inn', transfer['trading_org_inn'])
            loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
            loader.add_value('msg_number', transfer['msg_number'])
            loader.add_value('case_number', transfer['case_number'])
            loader.add_value('debtor_inn', transfer['debtor_inn'])
            loader.add_value('address', transfer['address'])
            loader.add_value('region', transfer['region'])
            loader.add_value('arbit_manager', transfer['arbit_manager'])
            loader.add_value('arbit_manager_inn', None)
            loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
            loader.add_value('status', combo.auc.get_status(table_=table))
            loader.add_value('start_date_requests', transfer['start_date_requests'])
            loader.add_value('end_date_requests', transfer['end_date_requests'])
            loader.add_value('start_date_trading', transfer['start_date_trading'])
            loader.add_value('end_date_trading', transfer['end_date_trading'])
            loader.add_value('lot_number', combo.auc.get_lot_number(table_=table))
            loader.add_value('short_name', combo.auc.get_short_name(table_=table))
            loader.add_value('lot_info', combo.auc.get_lot_info(table_=table))
            loader.add_value('property_information', combo.auc.get_property_info(table_=table))
            loader.add_value('start_price', combo.auc.get_start_price(table_=table))
            loader.add_value('step_price', combo.auc.get_step_price(table_=table))
            loader.add_value('created_at', return_parse_date())
            gen_dict = general_docs
            lot_dict = combo.doc.get_lot_docs(table_=table, full_path=self.full_path,
                                              relative_path=self.relative_path,
                                              main_url=self.main_url, _id=transfer['trading_id'],
                                              lot_num=''.join(loader.get_collected_values('lot_number')))
            total_dict = dict(chain.from_iterable(d.items() for d in (gen_dict, lot_dict)))
            loader.add_value('files', total_dict)
            yield loader.load_item()

        next_page = combo.offer.get_next_page_number()
        if next_page:
            try:
                if isinstance(int(next_page), int):
                    current_page += 1
                    link = re.sub(r'page=\d+', f'page={current_page}', link)
                    yield Request(link, callback=self.parse_auction_lot, dont_filter=True,
                                  cb_kwargs={'general_docs': general_docs,
                                             'current_page': current_page,
                                             'transfer': transfer, 'link': link})
            except Exception as e:
                logger.error(f'{response.url} :: ERROR NEXT PAGE {e}', exc_info=True)

    # OFFER ____________________________________
    def parse_offer_lot(self, response, transfer, general_docs, current_page, link):
        """ parse trades where trading type is OFFER """
        combo = Combo(response_=response)
        for table in combo.offer.get_lot_tables():
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', transfer['data_origin'])
            loader.add_value('trading_id', transfer['trading_id'])
            loader.add_value('trading_link', transfer['trading_link'])
            loader.add_value('trading_number', transfer['trading_number'])
            loader.add_value('trading_type', transfer['trading_type'])
            loader.add_value('trading_form', transfer['trading_form'])
            loader.add_value('trading_org', transfer['trading_org'])
            loader.add_value('trading_org_inn', transfer['trading_org_inn'])
            loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
            loader.add_value('msg_number', transfer['msg_number'])
            loader.add_value('case_number', transfer['case_number'])
            loader.add_value('debtor_inn', transfer['debtor_inn'])
            loader.add_value('address', transfer['address'])
            loader.add_value('region', transfer['region'])
            loader.add_value('arbit_manager', transfer['arbit_manager'])
            loader.add_value('arbit_manager_inn', None)
            loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
            loader.add_value('status', combo.auc.get_status(table_=table))
            loader.add_value('lot_number', combo.auc.get_lot_number(table_=table))
            loader.add_value('short_name', combo.auc.get_short_name(table_=table))
            loader.add_value('lot_info', combo.auc.get_lot_info(table_=table))
            loader.add_value('property_information', combo.auc.get_property_info(table_=table))
            loader.add_value('start_date_requests', combo.offer.start_date_request(table_=table))
            loader.add_value('end_date_requests', combo.offer.end_date_request(table_=table))
            loader.add_value('start_date_trading', combo.offer.start_date_trading(table_=table))
            loader.add_value('end_date_trading', combo.offer.end_date_trading(table_=table))
            loader.add_value('periods', combo.offer.get_period(table_=table))
            loader.add_value('start_price', combo.offer.start_price_offer(table_=table))
            loader.add_value('created_at', return_parse_date())
            gen_dict = general_docs
            lot_dict = combo.doc.get_lot_docs(table_=table, full_path=self.full_path,
                                              relative_path=self.relative_path,
                                              main_url=self.main_url, _id=transfer['trading_id'],
                                              lot_num=''.join(loader.get_collected_values('lot_number')))
            total_dict = dict(chain.from_iterable(d.items() for d in (gen_dict, lot_dict)))
            loader.add_value('files', total_dict)
            yield loader.load_item()

        next_page = combo.offer.get_next_page_number()
        if next_page:
            try:
                if isinstance(int(next_page), int):
                    current_page += 1
                    link = re.sub(r'page=\d+', f'page={current_page}', link)
                    yield Request(link, callback=self.parse_offer_lot, dont_filter=True,
                                  cb_kwargs={'general_docs': general_docs,
                                             'current_page': current_page,
                                             'transfer': transfer, 'link': link})
            except Exception as e:
                logger.error(f'{response.url} :: ERROR NEXT PAGE {e}', exc_info=True)

    def parse_competition_lot(self, response, transfer, general_docs, current_page, link):
        """ parse trades where trading type is AUCTION """
        combo = Combo(response_=response)
        for table in combo.auc.get_all_lot_tables():
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', transfer['data_origin'])
            loader.add_value('trading_id', transfer['trading_id'])
            loader.add_value('trading_link', transfer['trading_link'])
            loader.add_value('trading_number', transfer['trading_number'])
            loader.add_value('trading_type', transfer['trading_type'])
            loader.add_value('trading_form', transfer['trading_form'])
            loader.add_value('trading_org', transfer['trading_org'])
            loader.add_value('trading_org_inn', transfer['trading_org_inn'])
            loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
            loader.add_value('msg_number', transfer['msg_number'])
            loader.add_value('case_number', transfer['case_number'])
            loader.add_value('debtor_inn', transfer['debtor_inn'])
            loader.add_value('address', transfer['address'])
            loader.add_value('region', transfer['region'])
            loader.add_value('arbit_manager', transfer['arbit_manager'])
            loader.add_value('arbit_manager_inn', None)
            loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
            loader.add_value('status', combo.auc.get_status(table_=table))
            loader.add_value('start_date_requests', transfer['start_date_requests'])
            loader.add_value('end_date_requests', transfer['end_date_requests'])
            loader.add_value('start_date_trading', transfer['start_date_trading'])
            loader.add_value('end_date_trading', transfer['end_date_trading'])
            loader.add_value('lot_number', combo.auc.get_lot_number(table_=table))
            loader.add_value('short_name', combo.auc.get_short_name(table_=table))
            loader.add_value('lot_info', combo.auc.get_lot_info(table_=table))
            loader.add_value('property_information', combo.auc.get_property_info(table_=table))
            loader.add_value('start_price', combo.auc.get_start_price(table_=table))
            loader.add_value('step_price', combo.auc.get_step_price(table_=table))
            loader.add_value('created_at', return_parse_date())
            gen_dict = general_docs
            lot_dict = combo.doc.get_lot_docs(table_=table, full_path=self.full_path,
                                              relative_path=self.relative_path,
                                              main_url=self.main_url, _id=transfer['trading_id'],
                                              lot_num=''.join(loader.get_collected_values('lot_number')))
            total_dict = dict(chain.from_iterable(d.items() for d in (gen_dict, lot_dict)))
            loader.add_value('files', total_dict)
            yield loader.load_item()

        next_page = combo.offer.get_next_page_number()
        if next_page:
            try:
                if isinstance(int(next_page), int):
                    current_page += 1
                    link = re.sub(r'page=\d+', f'page={current_page}', link)
                    yield Request(link, callback=self.parse_competition_lot, dont_filter=True,
                                  cb_kwargs={'general_docs': general_docs,
                                             'current_page': current_page,
                                             'transfer': transfer, 'link': link})
            except Exception as e:
                logger.error(f'{response.url} :: ERROR NEXT PAGE {e}', exc_info=True)
