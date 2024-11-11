# -*- coding: utf-8 -*-
import re
from random import randint
from scrapy.spiders import Spider
from scrapy import Request, FormRequest
from itertools import chain
from ..utils.code_for_edit_and_format.working_with_time import return_parse_date
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.headers_for_spiders.spiders_header import headers_tender_ug as hd
from ..utils.post_data_for_spiders.bankrupt_electro_torgi_post_data import post_data_auction as pdac
from ..utils.post_data_for_spiders.bankrupt_electro_torgi_post_data import post_data_offer as pdao
from ..utils.post_data_for_spiders.bankrupt_electro_torgi_post_data import post_data_competition as pdcom
from ..utils.post_data_for_spiders.bankrupt_electro_torgi_post_data import post_data_offer_period as pdop
from ..utils.post_data_for_spiders.bankrupt_electro_torgi_post_data import post_data_auction_pagination as pdapag
from ..utils.post_data_for_spiders.arbitat_post_data import post_data_offer_period as pdop_without_doc
from ..manage_spiders.app import Combo
from ..utils.config import start_date_post, return_auction_link, data_origin, return_offer_link, return_compet_link, \
    tables
import copy
from ..utils.headers_for_spiders.generate_user_agent import USER_AGENT
from ..items import CrawlerItenderItem, CrawlerItenderItemLoader

import logging

logger = logging.getLogger(__name__)
TABLE = tables['table_tender_ug']


class TenderUgSpider(Spider):
    name = 'tender_ug'
    allowed_domains_ = ['bankrupt.tender.one']
    start_url = ['https://bankrupt.tender.one/']
    data_origin = data_origin['tender_ug']
    custom_settings = {
        # 'LOG_FILE': './tender_ug.log',
        'DOWNLOADER_MIDDLEWARES': {
            'crawler_itender.middlewares.CrawlerItenderDownloaderMiddleware': 543,
        },
        'ITEM_PIPELINES': {
            'crawler_itender.pipelines.CrawlerItenderPipeline': 300,
            'crawler_itender.pipelines.TenderUgDbConnect': 350,
        }

    }

    def __init__(self):
        super(TenderUgSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot(TABLE)

    def start_requests(self):
        yield Request(self.start_url[0], self.choose_datatype, headers=hd)

    def choose_datatype(self, response):
        for _type in ['auction', 'offer', 'competition']:
            if _type == 'auction':
                yield Request(return_auction_link(self.data_origin), self.parse_, headers=hd,
                              cb_kwargs={'_type': 'auction'})
            if _type == 'offer':
                yield Request(return_offer_link(self.data_origin), self.parse_, headers=hd,
                              cb_kwargs={'_type': 'offer'})
            if _type == 'competition':
                yield Request(return_compet_link(self.data_origin), self.parse_, headers=hd,
                              cb_kwargs={'_type': 'competition'})

    async def parse_(self, response, _type):
        first_post = None
        function_for_parse = None
        combo = Combo(response)
        if _type == 'auction':
            first_post = copy.deepcopy(pdac)
            function_for_parse = self.parse_serp_auction
            first_post[
                'ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_Датапроведенияс_dateInput'] = start_date_post
        if _type == 'offer':
            first_post = copy.deepcopy(pdao)
            function_for_parse = self.parse_serp_offer
            first_post[
                'ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_bidSubmissionStartDate_Датаначалапредставлениязаявокнаучастиес_dateInput'] = start_date_post
        if _type == 'competition':
            first_post = copy.deepcopy(pdcom)
            function_for_parse = self.parse_competiton_serp
            first_post[
                'ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_Датапроведенияс_dateInput'] = start_date_post

        first_post['__EVENTTARGET'] = combo.mpost.get_post_data_values(tag_html='input', post_argument='__EVENTTARGET')
        first_post['__EVENTARGUMENT'] = combo.mpost.get_post_data_values('input', '__EVENTARGUMENT')
        first_post['__CVIEWSTATE'] = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
        first_post['__VIEWSTATE'] = combo.mpost.get_post_data_values('input', '__VIEWSTATE')
        first_post['__EVENTVALIDATION'] = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
        yield FormRequest(response.url, formdata=first_post, headers=hd, callback=function_for_parse,
                          cb_kwargs={'first_post': first_post})

    # PARSE AUCTION
    def parse_serp_auction(self, response, first_post):
        """ parse serp of auction. fetch link to trading page"""
        combo = Combo(_response=response)
        eventvalidation = ''.join(re.findall(r'hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs',
                                             response.body.decode('utf-8')))
        cviewstate = ''.join(re.findall(r'hiddenField\|__CVIEWSTATE\|(.*)\|',
                                        response.body.decode('utf-8')))
        current_page = combo.serp.get_current_page()
        next_page = combo.serp.get_next_page()
        if combo.serp.body_scripts():
            data_next_page_post = combo.serp.body_scripts()
            first_post[
                'ctl00$ctl00$BodyScripts$BodyScripts$scripts'] = 'ctl00$ctl00$MainContent$ContentPlaceHolderMiddle$UpdatePanel2|' + data_next_page_post
            first_post['__CVIEWSTATE'] = cviewstate
            first_post['__EVENTVALIDATION'] = eventvalidation
            first_post['__EVENTTARGET'] = data_next_page_post
            if first_post.get("ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton", None):
                del first_post["ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"]
            first_post[''] = ''
            # GO TO TRADING PAGE
        for link in combo.serp.get_link_to_lot(current_page, self.data_origin):
            if link not in self.previous_lots:
                yield Request(link[0], callback=self.parse_trading_page_auction, headers=hd,
                              cb_kwargs={'lot_number': link[1], 'lot_link': link[2], 'attemp': 1}, dont_filter=True)

        if current_page and next_page:
            if int(current_page) < int(next_page):
                yield FormRequest(response.url, formdata=first_post, headers=hd,
                                  callback=self.parse_serp_auction,
                                  cb_kwargs={'first_post': first_post})

    async def parse_trading_page_auction(self, response, lot_number, lot_link, attemp):
        """parse trade page"""
        combo = Combo(_response=response)
        loader = CrawlerItenderItemLoader(CrawlerItenderItem(), response=response)
        loader.add_value('data_origin', self.data_origin)
        loader.add_value('trading_id', ''.join(re.findall(r'\d+', response.url)))
        loader.add_value('trading_link', response.url)
        loader.add_value('trading_number', combo.auc.get_trading_number_auction())
        loader.add_value('trading_type', 'auction')
        loader.add_value('trading_form', combo.auc.trading_form())
        loader.add_value('trading_org', combo.auc.get_organizer())
        loader.add_value('trading_org_inn', combo.auc.get_org_inn())
        loader.add_value('trading_org_contacts', combo.auc.return_org_contacts)
        loader.add_value('msg_number', combo.auc.msg_number)
        loader.add_value('case_number', combo.auc.case_number)
        loader.add_value('debtor_inn', combo.auc.get_debtor_inn())
        loader.add_value('arbit_manager', combo.auc.get_arbitr_name())
        loader.add_value('arbit_manager_inn', None)
        loader.add_value('arbit_manager_org', combo.auc.get_arbitr_company())
        loader.add_value('start_date_requests', combo.auc.start_date_request())
        loader.add_value('end_date_requests', combo.auc.end_date_request())
        loader.add_value('start_date_trading', combo.auc.start_date_trading())
        loader.add_value('end_date_trading', None)
        _id = ''.join(loader.get_collected_values('trading_id'))
        general_files = combo.offer.general_files(_id=_id, _data_origin=self.data_origin, host=self.allowed_domains_[0])
        hd_lot = copy.deepcopy(hd)
        hd_lot['referer'] = response.url
        hd_lot['user-agent'] = USER_AGENT
        # lot_info auction
        # lot_link = combo.auc.get_lot_link(lot_number, self.data_origin)
        pagination_on_page: list = combo.auc.pagination
        pdapag['__CVIEWSTATE'] = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
        pdapag['__EVENTVALIDATION'] = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
        pdapag['__EVENTTARGET'] = combo.serp.body_scripts()
        pdapag['__SCROLLPOSITIONY'] = str(randint(2289, 3662))
        yield Request(lot_link, callback=self.parse_lot_page,
                      headers=hd_lot, cb_kwargs={'loader': loader,
                                                 'lot_number': lot_number,
                                                 'general': general_files}, dont_filter=True)

    def parse_lot_page(self, response, loader, lot_number, general):
        """ parse lot page AUCTION"""
        combo = Combo(_response=response)
        lot_num = combo.auc.lot_number_on_lot_page(response.url, lot_number)
        if lot_number:
            loader.add_value('status', combo.auc.get_status_lot())
            loader.add_value('lot_id', ''.join(re.findall(r'\d+', str(response.url))))
            loader.add_value('lot_link', response.url)
            loader.add_value('lot_number', lot_num)
            loader.add_value('short_name', combo.auc.get_short_name())
            loader.add_value('lot_info', combo.auc.get_lot_info())
            loader.add_value('property_information', combo.auc.get_property_info())
            loader.add_value('start_price', combo.auc.start_price)
            loader.add_value('step_price', combo.auc.step_price)
            _id = ''.join(loader.get_collected_values('trading_id'))
            lot_file = combo.offer.lot_files(_data_origin=self.data_origin, _id=_id, lot_num=lot_number,
                                             host=self.allowed_domains_[0])
            if len(lot_file) == 0:
                lot_file['lot'] = list()
            if len(general) == 0:
                general['general'] = list()
            total_files = dict(chain(general.items(),
                                     lot_file.items()))
            loader.add_value('files', total_files)
            loader.add_value('created_at', return_parse_date())
            yield loader.load_item()

    # OFFER
    def parse_serp_offer(self, response, first_post):
        combo = Combo(_response=response)
        eventvalidation = ''.join(re.findall(r'hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs',
                                             response.body.decode('utf-8')))
        cviewstate = ''.join(re.findall(r'hiddenField\|__CVIEWSTATE\|(.*)\|',
                                        response.body.decode('utf-8')))
        current_page = combo.serp.get_current_page()
        next_page = combo.serp.get_next_page()
        if combo.serp.body_scripts():
            data_next_page_post = combo.serp.body_scripts()
            first_post[
                'ctl00$ctl00$BodyScripts$BodyScripts$scripts'] = 'ctl00$ctl00$MainContent$ContentPlaceHolderMiddle$UpdatePanel2|' + data_next_page_post
            first_post['__CVIEWSTATE'] = cviewstate
            first_post['__EVENTVALIDATION'] = eventvalidation
            first_post['__EVENTTARGET'] = data_next_page_post
            if first_post.get("ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton", None):
                del first_post["ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"]
            first_post[''] = ''
        # GO TO TRADING PAGE
        for link in combo.serp.get_link_to_lot(current_page, self.data_origin):
            if link not in self.previous_lots:
                yield Request(link[0], callback=self.parse_trade_page_offer, headers=hd,
                              cb_kwargs={'lot_number': link[1], 'lot_link': link[2], 'attemp': 1}, dont_filter=True)

        if current_page and next_page:
            if int(current_page) < int(next_page):
                yield FormRequest(response.url, formdata=first_post, headers=hd,
                                  callback=self.parse_serp_offer,
                                  cb_kwargs={'first_post': first_post})

    def parse_trade_page_offer(self, response, lot_number, lot_link, attemp):
        """parse trade page offer"""
        combo = Combo(_response=response)
        loader = CrawlerItenderItemLoader(CrawlerItenderItem(), response=response)
        loader.add_value('data_origin', self.data_origin)
        loader.add_value('trading_id', ''.join(re.findall(r'\d+', response.url)))
        loader.add_value('trading_link', response.url)
        loader.add_value('trading_number', combo.offer.get_trading_number_offer())
        loader.add_value('trading_type', 'offer')
        loader.add_value('trading_form', combo.offer.trading_form())
        loader.add_value('trading_org', combo.auc.get_organizer())
        loader.add_value('trading_org_inn', combo.auc.get_org_inn())
        loader.add_value('trading_org_contacts', combo.auc.return_org_contacts)
        loader.add_value('msg_number', combo.offer.msg_number)
        loader.add_value('case_number', combo.auc.case_number)
        loader.add_value('debtor_inn', combo.auc.get_debtor_inn())
        loader.add_value('arbit_manager', combo.auc.get_arbitr_name())
        loader.add_value('arbit_manager_inn', None)
        loader.add_value('arbit_manager_org', combo.auc.get_arbitr_company())
        _id = ''.join(loader.get_collected_values('trading_id'))
        general_files = combo.offer.general_files(_id=_id, _data_origin=self.data_origin,
                                                  host=self.allowed_domains_[0])
        hd_lot = copy.deepcopy(hd)
        hd_lot['referer'] = response.url
        hd_lot['user-agent'] = USER_AGENT

        # lot_info
        pagination_on_page: list = combo.auc.pagination
        pdapag['__CVIEWSTATE'] = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
        pdapag['__EVENTVALIDATION'] = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
        pdapag['__EVENTTARGET'] = combo.serp.body_scripts()
        pdapag['__SCROLLPOSITIONY'] = str(randint(2289, 3662))
        yield Request(lot_link, callback=self.parse_lot_page_offer,
                      headers=hd_lot, cb_kwargs={'loader': loader,
                                                 'lot_number': lot_number,
                                                 'general': general_files,
                                                 'pdata_lot_page_period': pdapag}, dont_filter=True)

    async def parse_lot_page_offer(self, response, loader, lot_number, general, pdata_lot_page_period):
        """ parse lot page """
        combo = Combo(_response=response)
        lot_num = combo.auc.lot_number_on_lot_page(response.url, lot_number)
        pager = combo.serp.get_href_post_lot_page()
        if lot_number and pager is None:
            loader.add_value('status', combo.auc.get_status_lot())
            loader.add_value('lot_id', ''.join(re.findall(r'\d+', str(response.url))))
            loader.add_value('lot_link', response.url)
            loader.add_value('lot_number', lot_num)
            loader.add_value('short_name', combo.auc.get_short_name())
            loader.add_value('lot_info', combo.auc.get_lot_info())
            loader.add_value('property_information', combo.offer.get_property_info())
            loader.add_value('periods', combo.offer.return_periods())
            loader.add_value('start_date_requests', combo.offer.start_date_request_offer)
            loader.add_value('end_date_requests', combo.offer.end_date_request_offer)
            loader.add_value('start_date_trading', combo.offer.start_date_trading_offer)
            loader.add_value('end_date_trading', combo.offer.end_date_trading_offer)
            loader.add_value('start_price', combo.offer.price_offer)
            _id = ''.join(loader.get_collected_values('trading_id'))
            lot_file = combo.offer.lot_files(_data_origin=self.data_origin, _id=_id, lot_num=lot_number,
                                             host=self.allowed_domains_[0])
            if len(lot_file) == 0:
                lot_file['lot'] = list()
            if len(general) == 0:
                general['general'] = list()
            total_files = dict(chain(general.items(),
                                     lot_file.items()))

            loader.add_value('files', total_files)
            loader.add_value('created_at', return_parse_date())
            yield loader.load_item()
        # IF LOT PAGE HAS MORE THEN 50 INTERVALS AND MORE THEN 1 PAGE
        else:
            _id = ''.join(loader.get_collected_values('trading_id'))
            lot_file = combo.offer.lot_files(_data_origin=self.data_origin, _id=_id, lot_num=lot_number,
                                             host=self.allowed_domains_[0])
            pages = combo.serp.fetch_pagination_links_lot_page()
            amount_of_page_period = len(pages) + 1
            # if 2 period pages on lot page or more
            hd_lot = copy.deepcopy(hd)
            hd_lot['referer'] = response.url
            hd_lot['user-agent'] = USER_AGENT
            cviewstate = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
            eventvalidation = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
            # first check value of two post param
            if cviewstate is None or len(cviewstate) < 0:
                cviewstate = ''.join(re.findall(r'hiddenField\|__CVIEWSTATE\|(.*)\|',
                                                response.body.decode('utf-8')))
                eventvalidation = ''.join(
                    re.findall(r'hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs',
                               response.body.decode('utf-8')))
            # second check value of two post param
            if cviewstate is None or len(cviewstate) < 0:
                cviewstate = pdata_lot_page_period['__CVIEWSTATE']
                eventvalidation = pdata_lot_page_period['__EVENTVALIDATION']
            pdop['__EVENTTARGET'] = combo.serp.body_scripts()
            pdop['__EVENTARGUMENT'] = pdata_lot_page_period['__EVENTARGUMENT']
            pdop['__CVIEWSTATE'] = cviewstate
            pdop['__VIEWSTATE'] = pdata_lot_page_period['__VIEWSTATE']
            pdop['__SCROLLPOSITIONY'] = pdata_lot_page_period['__SCROLLPOSITIONY']
            pdop['__EVENTVALIDATION'] = eventvalidation
            period_from_current_page = combo.offer.return_periods()
            post_query = pdop
            if len(lot_file) == 0:
                pdop_without_doc['__EVENTTARGET'] = combo.serp.body_scripts()
                pdop_without_doc['__EVENTARGUMENT'] = pdata_lot_page_period['__EVENTARGUMENT']
                pdop_without_doc['__CVIEWSTATE'] = cviewstate
                pdop_without_doc['__VIEWSTATE'] = pdata_lot_page_period['__VIEWSTATE']
                pdop_without_doc['__SCROLLPOSITIONY'] = pdata_lot_page_period['__SCROLLPOSITIONY']
                pdop_without_doc['__EVENTVALIDATION'] = eventvalidation
                post_query = pdop_without_doc
            yield FormRequest(response.url, callback=self.parse_lot_page_offer_next_page, formdata=post_query,
                              headers=hd_lot,
                              method='POST',
                              cb_kwargs={'loader': loader,
                                         'lot_number': lot_number,
                                         'general': general,
                                         'period_current_page': period_from_current_page,
                                         'pages': pages,
                                         'post_data_period': pdop}, dont_filter=True)

    async def parse_lot_page_offer_next_page(self, response, loader, lot_number, general, post_data_period,
                                             pages: list,
                                             period_current_page: list):
        """ parse next page with periods """
        combo = Combo(_response=response)
        pages.pop(0)
        if len(pages) > 0:
            hd_lot = copy.deepcopy(hd)
            hd_lot['referer'] = response.url
            hd_lot['user-agent'] = USER_AGENT
            cviewstate = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
            eventvalidation = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
            # first check value of two post param
            if cviewstate is None or len(cviewstate) < 0:
                cviewstate = ''.join(re.findall(r'hiddenField\|__CVIEWSTATE\|(.*)\|',
                                                response.body.decode('utf-8')))
                eventvalidation = ''.join(
                    re.findall(r'hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs',
                               response.body.decode('utf-8')))
            # second check value of two post param
            if cviewstate is None or len(cviewstate) < 0:
                cviewstate = post_data_period['__CVIEWSTATE']
                eventvalidation = post_data_period['__EVENTVALIDATION']
            pdop['__EVENTTARGET'] = combo.serp.body_scripts()
            pdop['__EVENTARGUMENT'] = post_data_period['__EVENTARGUMENT']
            pdop['__CVIEWSTATE'] = cviewstate
            pdop['__VIEWSTATE'] = post_data_period['__VIEWSTATE']
            pdop['__SCROLLPOSITIONY'] = post_data_period['__SCROLLPOSITIONY']
            pdop['__EVENTVALIDATION'] = eventvalidation
            period_from_current_page = combo.offer.return_periods()
            period_current_page.extend(period_from_current_page)
            yield FormRequest(response.url, callback=self.parse_lot_page_offer_next_page, formdata=pdop,
                              headers=hd_lot,
                              method='POST',
                              cb_kwargs={'loader': loader,
                                         'lot_number': lot_number,
                                         'general': general,
                                         'period_current_page': period_current_page,
                                         'pages': pages,
                                         'post_data_period': pdop}, dont_filter=True)
        else:
            error_ = combo.serp.find_error_page()
            if error_ is None:
                lot_num = combo.auc.lot_number_on_lot_page(response.url, lot_number)
                period_second_page = combo.offer.return_periods()
                full_periods = period_current_page
                for dict_ in period_second_page:
                    full_periods.append(dict_)
                loader.add_value('status', combo.auc.get_status_lot())
                loader.add_value('lot_id', ''.join(re.findall(r'\d+', str(response.url))))
                loader.add_value('lot_link', response.url)
                loader.add_value('lot_number', lot_num)
                loader.add_value('short_name', combo.auc.get_short_name())
                loader.add_value('lot_info', combo.auc.get_lot_info())
                loader.add_value('property_information', combo.offer.get_property_info())
                loader.add_value('periods', full_periods)
                start_date_request_offer = full_periods[0]['start_date_requests']
                end_date_request_offer = full_periods[-1]['end_date_requests']
                price_offer = full_periods[0]['current_price']
                loader.add_value('start_date_requests', start_date_request_offer)
                loader.add_value('end_date_requests', end_date_request_offer)
                loader.add_value('start_date_trading', start_date_request_offer)
                loader.add_value('end_date_trading', end_date_request_offer)
                loader.add_value('start_price', price_offer)
                _id = ''.join(loader.get_collected_values('trading_id'))
                lot_file = combo.offer.lot_files(_data_origin=self.data_origin, _id=_id, lot_num=lot_number,
                                                 host=self.allowed_domains_[0])
                if len(lot_file) == 0:
                    lot_file['lot'] = list()
                if len(general) == 0:
                    general['general'] = list()
                total_files = dict(chain(general.items(),
                                         lot_file.items()))

                loader.add_value('files', total_files)
                loader.add_value('created_at', return_parse_date())
                yield loader.load_item()
            else:
                logger.error(f'TWO PAGE PERIODS ERROR ERROR, {response.url}', exc_info=True)

    # COMPETITION
    def parse_competiton_serp(self, response, first_post):
        combo = Combo(_response=response)
        eventvalidation = ''.join(re.findall(r'hiddenField\|__EVENTVALIDATION\|(.*)\|.*\|asyncPostBackControlIDs',
                                             response.body.decode('utf-8')))
        cviewstate = ''.join(re.findall(r'hiddenField\|__CVIEWSTATE\|(.*)\|',
                                        response.body.decode('utf-8')))
        current_page = combo.serp.get_current_page()
        next_page = combo.serp.get_next_page()
        if combo.serp.body_scripts():
            data_next_page_post = combo.serp.body_scripts()
            first_post[
                'ctl00$ctl00$BodyScripts$BodyScripts$scripts'] = 'ctl00$ctl00$MainContent$ContentPlaceHolderMiddle$UpdatePanel2|' + data_next_page_post
            first_post['__CVIEWSTATE'] = cviewstate
            first_post['__EVENTVALIDATION'] = eventvalidation
            first_post['__EVENTTARGET'] = data_next_page_post
            if first_post.get("ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton", None):
                del first_post["ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton"]
            first_post[''] = ''
        # GO TO TRADING PAGE
        for link in combo.serp.get_link_to_lot(current_page, self.data_origin):
            if link not in self.previous_lots:
                yield Request(link[0], callback=self.parse_trade_page_competition, headers=hd,
                              cb_kwargs={'lot_number': link[1], 'lot_link': link[2], 'attemp': 1}, dont_filter=True)

        if current_page and next_page:
            if int(current_page) < int(next_page):
                yield FormRequest(response.url, formdata=first_post, headers=hd,
                                  callback=self.parse_competiton_serp,
                                  cb_kwargs={'first_post': first_post})

    # competition
    async def parse_trade_page_competition(self, response, lot_number, lot_link, attemp):
        """parse trade page offer"""
        combo = Combo(_response=response)
        loader = CrawlerItenderItemLoader(CrawlerItenderItem(), response=response)
        loader.add_value('data_origin', self.data_origin)
        loader.add_value('trading_id', ''.join(re.findall(r'\d+', response.url)))
        loader.add_value('trading_link', response.url)
        loader.add_value('trading_number', combo.compet.get_trading_number_comp())
        loader.add_value('trading_type', 'competition')
        loader.add_value('trading_form', combo.compet.trading_form())
        loader.add_value('trading_org', combo.auc.get_organizer())
        loader.add_value('trading_org_inn', combo.auc.get_org_inn())
        loader.add_value('trading_org_contacts', combo.auc.return_org_contacts)
        loader.add_value('msg_number', combo.compet.msg_number)
        loader.add_value('case_number', combo.auc.case_number)
        loader.add_value('debtor_inn', combo.auc.get_debtor_inn())
        loader.add_value('arbit_manager', combo.auc.get_arbitr_name())
        loader.add_value('arbit_manager_inn', None)
        loader.add_value('arbit_manager_org', combo.auc.get_arbitr_company())
        loader.add_value('start_date_requests', combo.compet.start_date_request())
        loader.add_value('end_date_requests', combo.compet.end_date_request())
        loader.add_value('start_date_trading', combo.compet.start_date_trading())
        loader.add_value('end_date_trading', None)
        hd_lot = copy.deepcopy(hd)
        hd_lot['referer'] = response.url
        hd_lot['user-agent'] = USER_AGENT
        _id = ''.join(loader.get_collected_values('trading_id'))
        general_files = combo.offer.general_files(_id=_id, _data_origin=self.data_origin, host=self.allowed_domains_[0])
        # lot_info auction
        # lot_link = combo.compet.get_lot_link(lot_number, self.data_origin)
        pagination_on_page: list = combo.auc.pagination
        pdapag['__CVIEWSTATE'] = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
        pdapag['__EVENTVALIDATION'] = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
        pdapag['__EVENTTARGET'] = combo.serp.body_scripts()
        pdapag['__SCROLLPOSITIONY'] = str(randint(2289, 3662))
        yield Request(lot_link, callback=self.parse_lot_page_competition,
                      headers=hd_lot, cb_kwargs={'loader': loader,
                                                 'lot_number': lot_number,
                                                 'general': general_files}, dont_filter=True)

    # competition
    def parse_lot_page_competition(self, response, loader, lot_number, general: dict):
        """ parse lot page Competition"""
        combo = Combo(_response=response)
        lot_num = combo.auc.lot_number_on_lot_page(response.url, lot_number)
        if lot_number:
            loader.add_value('status', combo.auc.get_status_lot())
            loader.add_value('lot_id', ''.join(re.findall(r'\d+', str(response.url))))
            loader.add_value('lot_link', response.url)
            loader.add_value('lot_number', lot_num)
            loader.add_value('short_name', combo.auc.get_short_name())
            loader.add_value('lot_info', combo.auc.get_lot_info())
            loader.add_value('property_information', combo.compet.get_property_info())
            loader.add_value('start_price', combo.auc.start_price)
            loader.add_value('step_price', combo.auc.step_price)
            _id = ''.join(loader.get_collected_values('trading_id'))
            lot_file = combo.offer.lot_files(_data_origin=self.data_origin, _id=_id, lot_num=lot_number,
                                             host=self.allowed_domains_[0])
            if len(lot_file) == 0:
                lot_file['lot'] = list()
            if len(general) == 0:
                general['general'] = list()
            total_files = dict(chain(general.items(),
                                     lot_file.items()))
            loader.add_value('files', total_files)
            loader.add_value('created_at', return_parse_date())
            yield loader.load_item()
