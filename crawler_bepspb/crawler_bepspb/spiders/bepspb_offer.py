# -*- coding: utf-8 -*-
import copy
import logging
import re
from itertools import chain
from random import randint

from scrapy import FormRequest, Request
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, SlotPolicy, SplashFormRequest

from ..items import CrawlerBepspbItem, CrawlerBepspbItemLoader
from ..manage_spiders.app import Combo
from ..utils.code_for_edit_and_format.working_with_time import return_parse_date
from ..utils.config import return_offer_link, data_origin, start_date_post
from ..utils.data_for_requests import script_lua, script_lua_nojs
# from ..utils.headers_for_spiders.generate_user_agent import USER_AGENT
# from ..utils.headers_for_spiders.spiders_header import headers_bepspb as hd
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.post_data_for_spiders.bepspb_post_data import post_data_auction_pagination as pdapag
from ..utils.post_data_for_spiders.bepspb_post_data import post_data_offer as pdao
from ..utils.post_data_for_spiders.bepspb_post_data import post_data_offer_period as pdop
from ..utils.post_data_for_spiders.bepspb_post_data import post_data_offer_period_ as pdop_without_doc

logger = logging.getLogger(__name__)


class BepspbSpider(Spider):
    name = 'bepspb_offer'
    allowed_domains = ['bepspb.ru']
    data_origin = data_origin['bepspb']
    start_url = ['https://bepspb.ru/']

    # start_url = ['https://bepspb.ru/public/auctions/view/15463/']

    def __init__(self):
        super(BepspbSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield SplashRequest(self.start_url[0], self.choose_datatype,
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
                            session_id=1,
                            )
        # for i in range(2):
        #     if i == 0:
        #         link_lot = 'https://bepspb.ru/public/auctions/lots/view/54427/'
        #         lot_number = 1
        #     elif i == 1:
        #         link_lot = 'https://bepspb.ru/public/auctions/lots/view/54428/'
        #         lot_number = 2
        #     # elif i == 2:
        #     #     link_lot = 'https://bepspb.ru/public/public-offers/lots/view/54912/'
        #     #     lot_number = 3
        #     # elif i == 3:
        #     #     link_lot = 'https://bepspb.ru/public/public-offers/lots/view/54913/'
        #     #     lot_number = 4
        #     else:
        #         return None
        #     yield SplashRequest(self.start_url[0], self.parse_trading_page_auction,
        #                         cache_args=['lua_source'], args={'lua_source': script_lua},
        #                         slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
        #                         session_id=1,
        #                         cb_kwargs={'lot_number': str(lot_number), 'lot_link': link_lot, 'attemp': 1}, dont_filter=True)

    def choose_datatype(self, response):
        for _type in ['offer']:
            if _type == 'offer':
                yield SplashRequest(return_offer_link(self.data_origin), self.parse_,
                                    cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
                                    slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True,
                                    cb_kwargs={'_type': 'offer'})

    async def parse_(self, response, _type):
        combo = Combo(response)
        if _type == 'offer':
            first_post = copy.deepcopy(pdao)
            function_for_parse = self.parse_serp_offer
            first_post[
                'ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_bidSubmissionStartDate_Датаначалапредставлениязаявокнаучастиес_dateInput'] = start_date_post
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

    # OFFER
    async def parse_serp_offer(self, response, first_post):
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
                yield Request(link[0], callback=self.parse_trade_page_offer,
                              cb_kwargs={'lot_number': link[1], 'lot_link': link[2], 'link_trade': link[0], 'attemp': 1},
                              dont_filter=True)

        if current_page and next_page:
            if int(current_page) < int(next_page):
                yield SplashFormRequest(response.url, formdata=first_post,
                                        cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
                                        slot_policy=SlotPolicy.PER_DOMAIN, dont_send_headers=True, dont_filter=True,
                                        callback=self.parse_serp_offer,
                                        cb_kwargs={'first_post': first_post})


    async def parse_trade_page_offer(self, response, lot_number, lot_link, link_trade, attemp):
        """parse trade page offer"""
        combo = Combo(_response=response)
        loader = CrawlerBepspbItemLoader(CrawlerBepspbItem(), response=response)
        loader.add_value('data_origin', self.data_origin)
        loader.add_value('trading_id', ''.join(re.findall(r'\d+', response.url)))
        loader.add_value('trading_link', response.url)
        try:
            trading_number = combo.offer.get_trading_number_offer()
        except:
            trading_number = None
        if trading_number is not None and attemp < 5:
            loader.add_value('trading_number', trading_number)
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
                                                      host=self.allowed_domains[0])
            # hd_lot = copy.deepcopy(hd)
            # hd_lot['referer'] = response.url
            # hd_lot['user-agent'] = USER_AGENT

            # lot_info
            pagination_on_page: list = combo.auc.pagination
            pdapag['__CVIEWSTATE'] = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
            pdapag['__EVENTVALIDATION'] = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
            pdapag['__EVENTTARGET'] = combo.serp.body_scripts()
            pdapag['__SCROLLPOSITIONY'] = str(randint(2289, 3662))
            yield Request(lot_link, callback=self.parse_lot_page_offer,
                          cb_kwargs={'loader': loader,
                                     'lot_number': lot_number,
                                     'general': general_files,
                                     'pdata_lot_page_period': pdapag,
                                     'lot_link': lot_link,
                                     'attemp2': 1}, dont_filter=True)
        else:
            attemp += 1
            yield Request(link_trade, callback=self.parse_trade_page_offer,
                          cb_kwargs={'lot_number': lot_number, 'lot_link': lot_link, 'link_trade': link_trade,
                                     'attemp': attemp}, dont_filter=True)

    async def parse_lot_page_offer(self, response, loader, lot_number, general, pdata_lot_page_period, lot_link,
                                   attemp2):
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
            _period = combo.offer.return_periods
            if _period is not None and attemp2 < 4:
                loader.add_value('periods', _period)
                loader.add_value('start_date_requests', combo.offer.start_date_request_offer)
                loader.add_value('end_date_requests', combo.offer.end_date_request_offer)
                loader.add_value('start_date_trading', combo.offer.start_date_trading_offer)
                loader.add_value('end_date_trading', combo.offer.end_date_trading_offer)
                loader.add_value('start_price', combo.offer.price_offer)
                _id = ''.join(loader.get_collected_values('trading_id'))
                lot_file = combo.offer.lot_files(_data_origin=self.data_origin, _id=_id, lot_num=lot_number,
                                                 host=self.allowed_domains[0])
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
                # if periods was not found
                attemp2 += 1
                yield Request(lot_link, callback=self.parse_lot_page_offer,
                              cb_kwargs={'loader': loader,
                                         'lot_number': lot_number,
                                         'general': general,
                                         'pdata_lot_page_period': pdata_lot_page_period,
                                         'lot_link': lot_link,
                                         'attemp2': attemp2}, dont_filter=True)
        # IF LOT PAGE HAS MORE THEN 50 INTERVALS AND MORE THEN 1 PAGE
        else:
            logger.critical(f'{response.url} :: ))))))))))) TEST FOR PERIODS')
            _id = ''.join(loader.get_collected_values('trading_id'))
            lot_file = combo.offer.lot_files(_data_origin=self.data_origin, _id=_id, lot_num=lot_number,
                                             host=self.allowed_domains[0])
            pages = combo.serp.fetch_pagination_links_lot_page()
            amount_of_page_period = len(pages) + 1
            # if 2 period pages on lot page or more
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
            period_from_current_page = combo.offer.return_periods
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
            period_from_current_page = combo.offer.return_periods
            period_current_page.extend(period_from_current_page)
            yield FormRequest(response.url, callback=self.parse_lot_page_offer_next_page, formdata=pdop,
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
                period_second_page = combo.offer.return_periods
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
                                                 host=self.allowed_domains[0])
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
