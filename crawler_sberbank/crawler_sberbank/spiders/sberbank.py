# -*- coding: utf-8 -*-
import base64
import logging

import pandas as pd
from bs4 import BeautifulSoup as BS
from icecream import ic
from scrapy import FormRequest, Request
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest, SlotPolicy
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import json
import xmltodict
import pprint

from ..items import SberbankItemLoader, CrawlerSberbankItem
from ..locators.locator_spider import LocatorSpider
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..trades.app import ComposeTrades
from ..utils.config import *
from ..utils.data_for_requests import script_lua_first_req, xml_data, script_trading, script_lot, script_lot_nojs, \
    simle_script_lua, simle2_script_lua, headers
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.manage_spider import *
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_time import increase_time_days, format_time, return_parse_date
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)

lst_links = list()
pp = pprint.PrettyPrinter(indent=4)


class SberbankSpider(CrawlSpider, ComposeTrades):
    def __init__(self, *args, **kwargs):
        super(SberbankSpider).__init__(*args, **kwargs)
        self.loc = LocatorSpider
        self.u_ = UrlConfig
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    name = 'sberbank'
    days_increase = time_delta
    http_user = 'parser'
    http_pass = 'gs:0Kh7%bD5$gBh}'

    def start_requests(self):
        """start requests according periods interval and frequency"""
        date_range = pd.date_range(start_time_from, periods=periods_, freq=format_period)
        for start_time in date_range:
            logger.info(f'THIS IS START TIME PUBLICATION - {start_time}')
            start_time = start_time.strftime('%d.%m.%Y %H:%M')
            time_from = "document.querySelector('input[name=PublicDateMin]').value='{}'".format(start_time)
            time_to = "document.querySelector('input[name=PublicDateMax]').value='{}'".format(
                f"{increase_time_days(start_time, self.days_increase)}")
            logger.info(f'THIS IS END DATE PUBLICATION:: {increase_time_days(start_time, self.days_increase)}')
            btn = "document.querySelector('input[type=button][value=Поиск]').click()"
            yield SplashRequest(main_url_start, self.make_second_request, endpoint='execute', encoding='utf-8',
                                cache_args=['lua_source'],
                                args={'lua_source': script_lua_first_req, 'headers': headers,
                                      'time_from': time_from, 'time_to': time_to, 'btn': btn, 'timeout': 60}, session_id=1,
                                meta={'time_from': start_time,
                                      'time_to': f"{increase_time_days(start_time, self.days_increase)}"},
                                dont_filter=True)

    def make_second_request(self, response):
        png_bytes = base64.b64decode(response.data["screenshot"])
        with open("screenshot.png", "wb") as f:
            f.write(png_bytes)

        import math
        """get full data for FormRequest and do it (get sum and amount of lots that period include)"""
        lot_count = response.xpath(self.loc.count_lots_page_loc).get()  # lot_count = 0
        # statistics - information about amount lots, total sum of lots and amount of organizers
        statistics = response.xpath(self.loc.statistics_loc).get()
        statistics = BS(statistics, features='lxml')

        total_lot = statistics.find('span', content='leaf:totalProc').get_text()
        total_lot = re.sub(r'^\s', '', total_lot).strip()
        try:
            total_sum = statistics.find('span', content='leaf:TotalSum').get_text()
            total_sum = re.sub(r'^\s', '', total_sum).strip()
        except:
            logger.error(f'{response.url} :: RESPONSE EMPTY :: total_sum - ERROR', exc_info=True)
            total_sum = None
        try:
            total_org = statistics.find('span', content='leaf:DistinctOrgs').get_text()
            total_org = re.sub(r'^\s', '', total_org).strip()
        except:
            logger.error(f'{response.url} :: RESPONSE EMPTY :: total_org - ERROR', exc_info=True)
            total_org = None
        # from_number - param to xml_data
        if total_lot:
            try:
                total_lot = int(total_lot)
            except:
                logger.critical(f'{response.url} :: RESPONSE EMPTY')
                total_lot = None

        if total_lot is not None and total_lot > 0:
            total_pages = math.ceil(total_lot / 100)
            for from_num in range(total_pages):
                xml_data_request = xml_data.format(start_date=response.meta['time_from'],
                                                   end_date=response.meta['time_to'],
                                                   total_lot=total_lot,
                                                   total_sum=total_sum,
                                                   total_org=total_org,
                                                   amount_lot_on_page='100',
                                                   from_number=str(from_num * 100))
                # number_of_iteration - when it will be equal total page then start parser lots
                yield FormRequest('https://utp.sberbank-ast.ru/Bankruptcy/SearchQuery/BidList', self.get_links_to_trade,
                                  formdata={
                                      'xmlData': xml_data_request,
                                      'orgId': '0',
                                      'buId': '0',
                                      'personId': '0',
                                      'buMainId': '0',
                                      'personMainId': '0'
                                  },
                                  # endpoint='execute', cache_args=['lua_source'],
                                  # args={'lua_source': script_lua}, method='POST',
                                  # session_id=1,
                                  meta={'total_lots_number': total_lot},
                                  headers={
                                      ':authority': 'utp.sberbank-ast.ru',
                                      ':method': 'POST',
                                      ':path': '/Bankruptcy/List/BidList',
                                      ':scheme': 'https',
                                      'accept': '*/*',
                                      'accept-encoding': 'gzip, deflate, br',
                                      'accept-language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
                                      'cache-control': 'no-cache',
                                      'content-type': 'application/x-www-form-urlencoded',

                                      'pragma': 'no-cache',
                                      'sec-fetch-dest': 'empty',
                                      'sec-fetch-mode': 'cors',
                                      'sec-fetch-site': 'same-origin',
                                      'x-requested-with': 'XMLHttpRequest',

                                  })

    def get_links_to_trade(self, response):
        """get links to trading page from response (json)"""
        global lst_links
        response = response
        res = json.loads(response.body)
        main_data = res.get('data').get('Data').get('data')
        main_data = json.loads(main_data)
        lots_data = main_data['hits']['hits']
        for lot in lots_data:
            lst_links.append(lot['_source']['objectHrefTerm'])
        if len(lst_links) == response.meta['total_lots_number']:
            lst_links_set = set(lst_links)
            for link in lst_links_set:
                link = str(link).replace('http', 'https').replace('httpss', 'https')
                path_headers = ''.join(re.findall(r'/Bankruptcy/NBT/PurchaseView/.+\d+$', link))
                headers_ = {':authority': 'utp.sberbank-ast.ru',
                            ':method': 'GET',
                            ':path': path_headers,
                            ':scheme': 'https',
                            'accept': '*/*',
                            #'accept-encoding': 'gzip, deflate, br',
                            'accept-language': 'n-US,en;q=0.9,ru-RU;q=0.8,ru;q=0.7,de-DE;q=0.6,de;q=0.5,uk-UA;q=0.4,uk;q=0.3,ro-RO;q=0.2,ro;q=0.1',
                            'cache-control': 'no-cache',
                            'content-type': 'application/x-www-form-urlencoded',
                            'origin': 'https://utp.sberbank-ast.ru',
                            'referer': 'https://utp.sberbank-ast.ru/Bankruptcy/List/BidList',
                            'pragma': 'no-cache',
                            'sec-fetch-dest': 'empty',
                            'sec-fetch-mode': 'cors',
                            'sec-fetch-site': 'same-origin',
                            'User-Agent': choice(agent_list)
                            }
                yield SplashRequest(link,
                                    callback=self.sort_trades,
                                    endpoint='execute',
                                    args={'lua_source': simle2_script_lua, 'headers': headers_})
                # yield Request(link, callback=self.sort_trades, headers=headers)

    def sort_trades(self, response):
        """get response and sort by type trading. Also get and structure ajax xml data"""
        soup = BS(str(response.text), features='lxml')
        # with open('response_explore.txt', 'w') as f:
        #     f.write(soup.decode('utf-8'))
        form_ajax_data = soup.find(attrs={'id': 'xmlData'})['value']
        convert_form_to_xml = BS(str(form_ajax_data), features='lxml-xml')
        convert_to_json = json.dumps(xmltodict.parse(str(convert_form_to_xml)), ensure_ascii=False)
        ajax_data_dict = json.loads(convert_to_json)
        # import pprint
        # pprint.pprint(ajax_data_dict)
        try:
            trading_type = sort_trading_type(dedent_func
                                             (ajax_data_dict['Purchase']['PurchaseTypeInfo']['PurchaseTypeName']))
            trading_form = get_trading_form(dedent_func
                                            (ajax_data_dict['Purchase']['PurchaseTypeInfo']['PurchaseTypeName']))
        except:
            logger.error(f'{response.url} :: INVALID DATA TRADING TYPE', exc_info=True)
            trading_type = None
            trading_form = None

        if str(trading_type) == 'auction':
            return self.parse_auction(response=response,
                                      trading_type=trading_type, trading_form=trading_form,
                                      ajax_data_dict=ajax_data_dict,
                                      form_ajax_data=form_ajax_data)

        if str(trading_type) == 'competition':
            return self.parse_auction(response=response,
                                      trading_type=trading_type, trading_form=trading_form,
                                      ajax_data_dict=ajax_data_dict,
                                      form_ajax_data=form_ajax_data)

        if str(trading_type) == 'offer':
            return self.parse_offer(response=response,
                                    trading_type=trading_type, trading_form=trading_form,
                                    ajax_data_dict=ajax_data_dict,
                                    form_ajax_data=form_ajax_data)

    def parse_auction(self, response, trading_type, trading_form, ajax_data_dict, form_ajax_data):
        combo = ComposeTrades(response_=response)
        lst_link_to_lots = list()
        try:
            lst_dict_lot_links = ajax_data_dict['Purchase']['Bids']['Bid']
        except:
            lst_dict_lot_links = None
            logger.error(f'{response.url} :: INVALID DATA LOT OR NO LOT')

        if isinstance(lst_dict_lot_links, list):
            lst_link_to_lots = list(map(lambda x: x['BidId'], lst_dict_lot_links))
        if isinstance(lst_dict_lot_links, dict):
            lst_link_to_lots = ajax_data_dict['Purchase']['Bids']['Bid']['BidId'].split()
        for link in lst_link_to_lots:
            # replace link to trade for link to lot
            _link = re.sub(part_path_to_trade, part_path_to_lot, str(response.url))
            _link = re.sub(r'\d+$', link, _link)
            # end replace link to trade for link to lot
            loader = SberbankItemLoader(CrawlerSberbankItem(), response=response)
            loader.add_value('data_origin', data_origin_url)
            loader.add_value('trading_id', combo.trading_id_auc(response.url))
            loader.add_value('trading_link', response.url)
            loader.add_value('trading_number', deep_get_dict(ajax_data_dict, 'Purchase.PurchaseInfo.PurchaseCode'))
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', trading_form)
            loader.add_value('msg_number', deep_get_dict(ajax_data_dict, 'Purchase.PurchaseInfo.IDEFRSB'))
            loader.add_value('trading_org', deep_get_dict(ajax_data_dict, 'Purchase.OrganizatorInfo.orgname'))
            loader.add_value('trading_org_inn', deep_get_dict(ajax_data_dict, 'Purchase.OrganizatorInfo.orginn'))
            loader.add_value('trading_org_contacts',
                             {'email:': deep_get_dict(
                                 ajax_data_dict, 'Purchase.OrganizatorInfo.orgemail', default=''),
                                 'phone': deep_get_dict(
                                     ajax_data_dict, 'Purchase.OrganizatorInfo.orgphone',
                                     default='')
                             })
            loader.add_value('case_number', deep_get_dict(ajax_data_dict, 'Purchase.BusinesInfo.businessno'))
            loader.add_value('debtor_inn', deep_get_dict(ajax_data_dict, 'Purchase.DebtorInfo.DebtorINN'))
            loader.add_value('arbit_manager', deep_get_dict(ajax_data_dict, 'Purchase.CrisicManagerInfo'
                                                                            '.crisicmanagerfullname'))
            loader.add_value('arbit_manager_inn',
                             deep_get_dict(ajax_data_dict, 'Purchase.CrisicManagerInfo.crisismanagerinn'))
            loader.add_value('arbit_manager_org', deep_get_dict(ajax_data_dict, 'Purchase.CrisicManagerInfo'
                                                                                '.arbitrageorganizationpanel'
                                                                                '.arbitrageorganizationname'))

            # start date request
            try:
                loader.add_value('start_date_requests', format_time(deep_get_dict(ajax_data_dict, 'Purchase.RequestInfo'
                                                                                                  '.RequestStartDate')))
            except:
                loader.add_value('start_date_requests', None)
                logger.error(f'{response.url} :: INVALID DATA START DATE REQUEST AUCTION')
            # end date request
            try:
                loader.add_value('end_date_requests', format_time(deep_get_dict(ajax_data_dict, 'Purchase.RequestInfo'
                                                                                                '.RequestStopDate')))
            except:
                loader.add_value('end_date_requests', None)
                logger.error(f'{response.url} :: INVALID DATA END DATE REQUEST AUCTION')
            # start date trading
            try:
                loader.add_value('start_date_trading', format_time(deep_get_dict(ajax_data_dict, 'Purchase.Terms'
                                                                                                 '.PurchaseAuctionStartDate')))
            except:
                loader.add_value('start_date_trading', None)
                logger.error(f'{response.url} :: INVALID START DATE TRADING AUCTION')
            # end date trading
            try:
                loader.add_value('end_date_trading', format_time(deep_get_dict(ajax_data_dict, 'Purchase.ResultInfo'
                                                                                               '.AuctionResultDate')))
            except:
                loader.add_value('end_date_trading', None)
                logger.error(f'{response.url} :: INVALID END DATE TRADING AUCTION')

            url = _link
            # if url == 'https://utp.sberbank-ast.ru/Bankruptcy/NBT/BidView/11/0/0/996841':
            if url not in self.previous_lots:
                files_general = combo.offer.download_general(combo.trading_id_auc(response.url), form_ajax_data)
                yield SplashRequest(url,
                                    callback=self.parse_auction_lot,

                                    endpoint='execute',
                                    args={'lua_source': simle_script_lua, 'headers': headers},
                                    # 'css': '#xmlData',
                                    # 'maxwait': 0.2},
                                    session_id=1,
                                    cb_kwargs={'loader': loader, 'files': files_general},
                                    errback=self.errback_httpbin
                                    )

    def parse_auction_lot(self, response, loader, files):
        combo = ComposeTrades(response_=response)
        soup = BS(str(response.body.decode('utf-8')), features='lxml')
        form_ajax_data = soup.find(attrs={'id': 'xmlData'})['value']
        loader.add_value('lot_id', combo.auc.get_lot_id)
        loader.add_value('lot_link', combo.auc.get_lot_link)
        loader.add_value('lot_number', combo.auc.get_lot_number)
        loader.add_value('short_name', combo.auc.get_short_name)
        loader.add_value('lot_info', combo.auc.get_lot_info)
        loader.add_value('property_information', combo.auc.get_property_info)
        loader.add_value('start_price', combo.auc.get_start_price)
        loader.add_value('step_price', combo.auc.get_step_price)
        files_lot = combo.offer.download_general(combo.auc.get_lot_id, form_ajax_data)
        loader.add_value('files', {'general': files, 'lot': files_lot})
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()

    def parse_offer(self, response, trading_type, trading_form, ajax_data_dict, form_ajax_data):
        """parse trades with type offer. Using the same methods from auction class"""
        combo = ComposeTrades(response_=response)
        # according  for type( depends of amount of lots) the lst_link_to_lots will be the instance of that type
        lst_link_to_lots = None
        try:
            lst_dict_lot_links = ajax_data_dict['Purchase']['Bids']['Bid']
        except:
            lst_dict_lot_links = None
            logger.error(f'{response.url} :: INVALID DATA LOT OR NO LOT')
        if isinstance(lst_dict_lot_links, list):
            lst_link_to_lots = list(map(lambda x: x['BidId'], lst_dict_lot_links))
        if isinstance(lst_dict_lot_links, dict):
            lst_link_to_lots = ajax_data_dict['Purchase']['Bids']['Bid']['BidId'].split()
        for link in lst_link_to_lots:
            # replace link to trade for link to lot
            _link = re.sub(part_path_to_trade, part_path_to_lot, str(response.url))
            _link = re.sub(r'\d+$', link, _link)
            loader = SberbankItemLoader(CrawlerSberbankItem(), response=response)
            loader.add_value('data_origin', data_origin_url)
            loader.add_value('trading_id', combo.trading_id_auc(response.url))
            loader.add_value('trading_link', response.url)
            loader.add_value('trading_number', deep_get_dict(ajax_data_dict, 'Purchase.PurchaseInfo.PurchaseCode'))
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', trading_form)
            loader.add_value('msg_number', deep_get_dict(ajax_data_dict, 'Purchase.PurchaseInfo.IDEFRSB'))
            loader.add_value('trading_org', deep_get_dict(ajax_data_dict, 'Purchase.OrganizatorInfo.orgname'))
            loader.add_value('trading_org_inn', deep_get_dict(ajax_data_dict, 'Purchase.OrganizatorInfo.orginn'))
            loader.add_value('trading_org_contacts', {'email:':
                deep_get_dict(
                    ajax_data_dict, 'Purchase.OrganizatorInfo.orgemail', default=''),
                'phone':
                    deep_get_dict(
                        ajax_data_dict, 'Purchase.OrganizatorInfo.orgphone',
                        default='')
            })
            loader.add_value('case_number', deep_get_dict(ajax_data_dict, 'Purchase.BusinesInfo.businessno'))
            loader.add_value('debtor_inn', deep_get_dict(ajax_data_dict, 'Purchase.DebtorInfo.DebtorINN'))
            loader.add_value('arbit_manager', deep_get_dict(ajax_data_dict, 'Purchase.CrisicManagerInfo'
                                                                            '.crisicmanagerfullname'))
            loader.add_value('arbit_manager_inn',
                             deep_get_dict(ajax_data_dict, 'Purchase.CrisicManagerInfo.crisismanagerinn'))
            loader.add_value('arbit_manager_org', deep_get_dict(ajax_data_dict, 'Purchase.CrisicManagerInfo'
                                                                                '.arbitrageorganizationpanel'
                                                                                '.arbitrageorganizationname'))
            # end replace link to trade for link to lot
            url = _link
            if url not in self.previous_lots:
                files_general = combo.offer.download_general(combo.trading_id_auc(response.url), form_ajax_data)
                yield SplashRequest(url,
                                    callback=self.parse_offer_lot,
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    args={'lua_source': simle_script_lua, 'headers': headers},
                                    endpoint='execute',
                                    session_id=1,
                                    cb_kwargs={'loader': loader, 'files': files_general},
                                    errback=self.errback_httpbin,
                                    )

    def parse_offer_lot(self, response, loader, files):
        combo = ComposeTrades(response_=response)
        soup = BS(str(response.body.decode('utf-8')), features='lxml')
        form_ajax_data = soup.find(attrs={'id': 'xmlData'})['value']
        loader.add_value('lot_id', combo.auc.get_lot_id)
        loader.add_value('lot_link', combo.auc.get_lot_link)
        loader.add_value('lot_number', combo.auc.get_lot_number)
        loader.add_value('short_name', combo.auc.get_short_name)
        loader.add_value('lot_info', combo.auc.get_lot_info)
        loader.add_value('property_information', combo.auc.get_property_info)
        loader.add_value('start_date_requests', combo.offer.start_date_request)
        loader.add_value('end_date_requests', combo.offer.end_date_request)
        loader.add_value('start_date_trading', combo.offer.start_date_trading)
        loader.add_value('end_date_trading', combo.offer.end_date_trading)
        loader.add_value('start_price', combo.offer.start_price)
        loader.add_value('periods', combo.offer.periods_return)
        files_lot = combo.offer.download_general(combo.auc.get_lot_id, form_ajax_data)
        loader.add_value('files', {'general': files, 'lot': files_lot})
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()

    def errback_httpbin(self, failure):
        # logs failures

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError occurred on %s", response.url)

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError occurred on %s", request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError occurred on %s", request.url)
