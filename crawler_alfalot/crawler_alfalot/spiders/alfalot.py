# -*- coding: utf-8 -*-
import copy
import logging
import re
from itertools import chain
from random import randint

from icecream import ic
from scrapy import FormRequest, Request
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, SlotPolicy, SplashFormRequest

from ..items import CrawlerAlfalotItem, CrawlerAlfalotItemLoader
from ..manage_spiders.app import Combo
from ..utils.code_for_edit_and_format.working_with_time import return_parse_date
from ..utils.config import return_auction_link, data_origin, start_date_post
from ..utils.data_for_requests import script_lua, script_lua_nojs
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.headers_for_spiders.generate_user_agent import USER_AGENT
from ..utils.headers_for_spiders.spiders_header import headers_alfalot as hd
from ..utils.post_data_for_spiders.alfalot_post_data import post_data_auction as pdac
from ..utils.post_data_for_spiders.alfalot_post_data import post_data_auction_pagination as pdapag

logger = logging.getLogger(__name__)


class AlfalotSpider(Spider):
    name = 'alfalot'
    allowed_domains_ = ['bankrupt.alfalot.ru']
    data_origin = data_origin['alfalot']
    start_url = ['https://bankrupt.alfalot.ru/']

    def __init__(self):
        super(AlfalotSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield SplashRequest(self.start_url[0], self.choose_datatype, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True
                            )

    def choose_datatype(self, response):
        for _type in ['auction']:
            if _type == 'auction':
                yield SplashRequest(return_auction_link(self.data_origin), self.parse_,
                                    cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
                                    slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
                                    cb_kwargs={'_type': 'auction'})

    async def parse_(self, response, _type):
        combo = Combo(response)
        if _type == 'auction':
            first_post = copy.deepcopy(pdac)
            function_for_parse = self.parse_serp_auction
            first_post[
                'ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_Датапроведенияс_dateInput'] = start_date_post

        else:
            first_post = None
            function_for_parse = None
        first_post['__EVENTTARGET'] = combo.mpost.get_post_data_values(tag_html='input', post_argument='__EVENTTARGET')
        first_post['__EVENTARGUMENT'] = combo.mpost.get_post_data_values('input', '__EVENTARGUMENT')
        first_post['__CVIEWSTATE'] = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
        first_post['__VIEWSTATE'] = combo.mpost.get_post_data_values('input', '__VIEWSTATE')
        first_post['__EVENTVALIDATION'] = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
        yield SplashFormRequest(response.url, formdata=first_post,
                                cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
                                slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
                                callback=function_for_parse,
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
                yield Request(link[0],
                              callback=self.parse_trading_page_auction,
                              cb_kwargs={'lot_number': link[1], 'lot_link': link[2], 'link_trade': link[0], 'attemp': 1}, dont_filter=True)
                # yield SplashRequest(link[0], callback=self.parse_trading_page_auction, endpoint='execute',
                #                     cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
                #                     slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
                #                     cb_kwargs={'lot_number': link[1], 'lot_link': link[2],
                #                                'link_trade': link[0], 'attemp': 1}, dont_filter=True)

        if current_page and next_page:
            if int(current_page) < int(next_page):
                yield FormRequest(response.url, formdata=first_post,
                                  callback=self.parse_serp_auction,
                                  cb_kwargs={'first_post': first_post}, dont_filter=True)
                # yield SplashFormRequest(response.url, formdata=first_post,
                #                         callback=self.parse_serp_auction, endpoint='execute',
                #                         cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
                #                         slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
                #                         cb_kwargs={'first_post': first_post}, dont_filter=True)

    async def parse_trading_page_auction(self, response, lot_number, lot_link, link_trade, attemp):
        """parse trade page"""
        combo = Combo(_response=response)
        loader = CrawlerAlfalotItemLoader(CrawlerAlfalotItem(), response=response)
        loader.add_value('data_origin', self.data_origin)
        loader.add_value('trading_id', ''.join(re.findall(r'\d+', response.url)))
        loader.add_value('trading_link', response.url)
        try:
            trading_number = combo.auc.get_trading_number_auction()
        except:
            trading_number = None
        if trading_number is not None and attemp < 5:
            loader.add_value('trading_number', trading_number)
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
            start_date_trading = combo.auc.start_date_trading()
            # if start_date_trading is not None and attemp < 5:
            loader.add_value('start_date_requests', combo.auc.start_date_request())
            loader.add_value('end_date_requests', combo.auc.end_date_request())
            loader.add_value('start_date_trading', start_date_trading)
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
                          cb_kwargs={'loader': loader,
                                     'lot_number': lot_number,
                                     'general': general_files,
                                     }, dont_filter=True)
            # yield SplashRequest(lot_link, callback=self.parse_lot_page, endpoint='execute',
            #                     cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
            #                     slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
            #                     cb_kwargs={'loader': loader,
            #                                'lot_number': lot_number,
            #                                'general': general_files,
            #                                }, dont_filter=True)
        else:
            attemp += 1
            yield SplashRequest(link_trade, callback=self.parse_trading_page_auction,
                                cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
                                slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
                                cb_kwargs={'lot_number': lot_number, 'lot_link': lot_link, 'link_trade': link_trade,
                                           'attemp': attemp}, dont_filter=True)

    async def parse_lot_page(self, response, loader, lot_number, general: dict):
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
