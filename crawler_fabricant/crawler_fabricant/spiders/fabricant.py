# -*- coding: utf-8 -*-
import re
import urllib.parse

from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from scrapy_splash import SplashFormRequest, SlotPolicy

from general_utils import CrawlerBankruptItem, CrawlerBankruptItemLoader
from general_utils.config import lst_exet
from general_utils.location import Region
from ..app import Combo
from ..trades.lot import LotParse
from ..utils.data_for_requests import *
from ..utils.spider_manage import *
from ..utils.working_with_url import UrlConfig
from ..utils.working_with_time import *
from ..utils.work_with_path_and_dir import LotFilesDir, GeneralFilesDir
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.work_with_text_and_number import get_price, get_lot_num_simple
from ..utils.config import *
from ..utils.download import DownloadFiles
from ..locators.spider_locators import *
from scrapy import Request
import pathlib
from bs4 import BeautifulSoup as BS
import logging
from ..trades.offer import OfferParse
from ..trades.combo_auction import ComboAuctionCompetition

logger = logging.getLogger(__name__)


class FabrikantSpider(CrawlSpider, DownloadFiles, OfferParse, ComboAuctionCompetition, LotFilesDir, UrlConfig):
    name = 'fabrikant'
    # allowed_domains = ['fabrikant.ru']
    start_urls = start_url.split()

    def __init__(self):
        super(FabrikantSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()

    def start_requests(self):
        yield SplashRequest(
            start_url, self.start_requests_query, endpoint='execute',
            cache_args=['lua_source'], args={'lua_source': script_lua},
            slot_policy=SlotPolicy.PER_DOMAIN,
            session_id=1,
            errback=self.errback_httpbin
        )

    def start_requests_query(self, response):
        soup = BS(response.text, 'lxml')
        formdata['type_hash'] = soup.find(attrs={'id': 'type_hash'})['value']
        yield SplashFormRequest.from_response(
            response=response,
            url=response.url,
            formdata=formdata, callback=self.parse,
            meta={'current_page': 1}
        )

    def parse(self, response, all_links: set = None):
        current_page = response.meta['current_page']
        links = response.css('.marketplace-unit.ready h4 a::attr(href)').getall()
        all_links = (all_links or set()).union(links)
        next_page = response.xpath(pagination_button_loc).get()
        if next_page:
            next_page = BS(str(next_page), features='lxml')
            link = data_origin_url + ''.join(next_page.a['href'])
            parse_link = urllib.parse.parse_qs(urllib.parse.urlsplit(link).query)
        if next_page and int(current_page) < int(''.join(parse_link['page'])):
            yield SplashRequest(
                link, self.parse,
                endpoint='execute',
                cache_args=['lua_source'],
                args={'lua_source': script_lua},
                slot_policy=SlotPolicy.PER_DOMAIN,
                session_id=1, errback=self.errback_httpbin,
                meta={'current_page': ''.join(parse_link['page'])},
                cb_kwargs={'all_links': all_links}
            )
        else:
            for link in all_links:
                link = link.replace('https://fabrikant.ru', 'https://www.fabrikant.ru')
                yield Request(link, self.parse_trade)

    # PARSE AUCTION (ONE LOT)
    def parse_auction(self, response):
        combo = ComboAuctionCompetition(response_=response)
        lot_number = combo.auc.get_lot_number(response.url)
        loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
        loader.add_value('data_origin', combo.auc.data_origin_auction)
        loader.add_value('trading_id', combo.auc.trading_id_auction(response.url))
        loader.add_value('trading_link', combo.auc.trading_link_auction(response.url))
        trad_link = ''.join(loader.get_collected_values('trading_link'))
        if (trad_link, lot_number) not in self.previous_lots:
            loader.add_value('trading_number', combo.auc.trading_number_auction(response.url))
            loader.add_value('trading_type', check_trading_type(combo.auc.trading_type_auction(response.url)))
            loader.add_value('trading_form', check_trading_form(combo.auc.trading_form_auction(response.url)))
            loader.add_value('trading_org', combo.auc.trading_org_auction(response.url))
            loader.add_value('msg_number', combo.auc.msg_number(response.url))
            loader.add_value('case_number', combo.auc.case_number(response.url))
            loader.add_value('debtor_inn', combo.auc.debitor_inn(response.url))
            address = combo.auc.address(response.url)
            region = None
            if address:
                region = Region.get_region(address)
            loader.add_value('address', address)
            loader.add_value('region', region)
            loader.add_value('arbit_manager', combo.auc.arbitr_manager(response.url))
            loader.add_value('arbit_manager_inn', combo.auc.arbitr_manag_inn(response.url))
            loader.add_value('arbit_manager_org', combo.auc.arbitr_org())
            loader.add_value('status', response.meta['status'])
            # _LOT_INFO_
            loader.add_value('lot_number', lot_number)
            loader.add_value('short_name', combo.auc.short_name(response.url))
            loader.add_value('property_information', combo.auc.property_info)
            # _WORKING_WITH_DATES_AUCTION_
            loader.add_value('start_date_requests', combo.auc.start_date_request(response.url))
            loader.add_value('end_date_requests', combo.auc.end_date_request(response.url))
            loader.add_value('start_date_trading', combo.auc.start_date_trading(response.url))
            loader.add_value('end_date_trading', combo.auc.end_date_trading(response.url))
            if loader.get_collected_values('start_date_trading') \
                    is None and loader.get_collected_values('end_date_trading') is None:
                logger.error(f'{response.url}:: CHECK AUCTION ABSENT DATA _ START TRADING AND END TRADING')
            # _WORKING_WITH_PRICES_
            loader.add_value('start_price', combo.auc.start_price(response.url))
            loader.add_value('step_price', combo.auc.get_step_price(response.url))
            if loader.get_collected_values('start_price') \
                    is None and loader.get_collected_values('step_price') is None:
                logger.error(f'{response.url}:: CHECK AUCTION START & STEP PRICES')
            # _GET_LINK_TO_TRADING_ORGANIZER_CONTACTS_
            link_to_org = combo.auc.get_link_to_org_info
            # _GET_LINK_TO_DOCUMENTS_AUCTION_
            link_to_document = combo.auc.link_doc_page(response.url)
            referer_ = response.url
            yield Request(url=link_to_org, callback=self.parse_auction_organizer, dont_filter=True,
                          cb_kwargs={'loader': loader, 'referer': referer_,
                                     'link_to_document': link_to_document})

    def parse_auction_organizer(self, response, loader, referer, link_to_document):
        combo = ComboAuctionCompetition(response_=response)
        referer_ = referer
        loader.add_value('trading_org_inn', combo.auc.trading_org_inn)
        loader.add_value('trading_org_contacts',
                         {'email': combo.auc.trading_org_email(), 'phone': combo.auc.get_phone_org()})

        yield Request(url=link_to_document, callback=self.documentation_auction, dont_filter=True,
                      cb_kwargs={'loader': loader}
                      )

    def documentation_auction(self, response, loader):
        load = DownloadFiles()
        u = UrlConfig()
        combo = ComboAuctionCompetition(response_=response)
        lot = list()
        general = list()
        for tr in combo.auc.table_without_thead:
            relative_path_f = ''
            original_name = combo.auc.original_name_file(tr)
            link_etp = combo.auc.document_link(tr)
            if pathlib.Path(''.join(original_name)).suffix in lst_exet \
                    or ''.join(filter(lambda x: x in link_etp, list(map(lambda y: y, lst_exet)))):
                combo.auc.create_dir()
                relative_path_f = combo.auc.name_file_in_db(response.url, original_name)
                name_on_server = combo.auc.name_file_on_server(response.url, original_name)
                load.request_to_download(url=link_etp, referer=response.url, original_name=name_on_server)
            general.append({'original_name': original_name,
                            'link': relative_path_f,
                            'link_etp': u.parse_url(link_etp)})
        total_files = {'general': general, 'lot': lot}
        loader.add_value('files', total_files)
        loader.add_value('created_at', return_parse_date())
        return loader.load_item()

    # END PARSE AUCTION (ONE LOT)

    # __PARSE__OAZF__AUCTION_
    def parse_oazf_auction(self, response):
        referer_main = response.meta['referer_main']
        referer_ = response.url
        trading_form = response.meta['trading_form']
        status = response.meta['status']
        combo = ComboAuctionCompetition(response_=response)
        all_lots = response.css(oazf_lots_loc).getall()
        link_to_organizer = combo.oazf.get_link_to_org_info
        link_to_document = combo.auc.link_doc_page(response.url)
        # dictionary with general documents
        lst_trade_doc = self.parse_general_doc_oazf(link_to_document, referer_)
        for lot in all_lots:
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', combo.auc.data_origin_auction)
            loader.add_value('trading_id', combo.auc.trading_id_auction(response.url))
            loader.add_value('trading_link', combo.oazf.get_lot_link(lot))
            loader.add_value('trading_number', combo.oazf.get_trading_num_oazf(lot, response.url))
            loader.add_value('trading_type', 'auction')
            loader.add_value('trading_form', 'auction')
            loader.add_value('trading_org', combo.oazf.trading_org_oazf(response.url))
            loader.add_value('msg_number', combo.oazf.msg_number(response.url))
            loader.add_value('case_number', combo.oazf.case_number(response.url))
            loader.add_value('debtor_inn', combo.oazf.debitor_inn)
            loader.add_value('arbit_manager', combo.oazf.arbitr_manager_oazf(response.url))
            loader.add_value('arbit_manager_inn', combo.oazf.arbitr_inn_oazf)
            loader.add_value('arbit_manager_org', combo.oazf.arbitr_org_oazf(response.url))
            loader.add_value('status', status)
            loader.add_value('lot_number', combo.oazf.get_lot_number(lot, response.url))
            loader.add_value('lot_link', None)
            loader.add_value('short_name', combo.oazf.short_name_main(lot, response.url))
            loader.add_value('property_information', combo.oazf.property_info_lot(lot, response.url))
            loader.add_value('start_date_requests', combo.oazf.start_date_request_oazf(lot, response.url))
            loader.add_value('end_date_requests', combo.oazf.end_date_request_oazf(lot, response.url))
            loader.add_value('start_date_trading', combo.oazf.start_date_trading_oazf(lot, response.url))
            loader.add_value('end_date_trading', combo.oazf.end_date_trading_oazf(lot, response.url))
            loader.add_value('start_price', combo.oazf.start_price_oazf(lot, response.url))
            request = Request(url=link_to_organizer, callback=self.parse_oazf_org_info, dont_filter=True,
                              cb_kwargs={'loader': loader, 'referer': referer_,
                                         'link_to_document': link_to_document, 'general': lst_trade_doc, 'lot_': lot},
                              meta={'trading_form': trading_form})
            yield request

    # _EXTRA METHOD FOR FETCH DOCUMENTS OAZF. REASON - IF WE HAVE MANY LOTS IT WILL BE ONLY ONE REQUEST TO GENERAL DOC
    def parse_general_doc_oazf(self, link, referer):
        u = UrlConfig()
        download = DownloadFiles()
        instance_general = GeneralFilesDir()
        page_response = download.make_request(link, referer)
        soup = BS(page_response, 'lxml')
        general = list()
        table = soup.find_all('table', class_="list document_list")
        tr_ = BS(str(table), features='lxml').find_all('tr', class_=lambda x: x != "thead")
        for tr in tr_:
            relative_path_f = ''
            original_name = dedent_func(BS(str(tr), features='lxml').find('td').find_next('td').find('b').get_text())
            link_etp = BS(str(tr), features='lxml').find('td').find_next('td').find('a').get('href')
            if pathlib.Path(''.join(original_name)).suffix in lst_exet \
                    or ''.join(filter(lambda x: x in link_etp, list(map(lambda y: y, lst_exet)))):
                name_on_server = instance_general.extra_file_name(link, original_name)
                relative_path_f = instance_general.extra_file_name_in_db(name_on_server)
                if data_origin_url not in link_etp:
                    link_etp = data_origin_url + link_etp
                download.request_to_download(url=link_etp, referer=referer, original_name=name_on_server)
            general.append({'original_name': original_name,
                            'link': relative_path_f,
                            'link_etp': u.parse_url(link_etp)})
        return general

    def parse_oazf_org_info(self, response, loader, referer, link_to_document, general, lot_):
        referer_ = referer
        combo = ComboAuctionCompetition(response_=response)
        link_to_document = link_to_document
        loader.add_value('trading_org_inn', combo.auc.trading_org_inn)
        loader.add_value('trading_org_contacts',
                         {'email': combo.auc.trading_org_email(), 'phone': combo.auc.get_phone_org()})
        yield Request(url=link_to_document, callback=self.lot_document_oazf, dont_filter=True,
                      cb_kwargs={'loader': loader, 'general': general, 'lot_': lot_},

                      )

    def lot_document_oazf(self, response, loader, general, lot_):
        load = DownloadFiles()
        u = UrlConfig()
        combo = ComboAuctionCompetition(response_=response)
        lot = list()
        table_lot_doc = combo.oazf.table_without_thead(lot_)
        if table_lot_doc:
            for tr in table_lot_doc:
                relative_path_f = ''
                original_name = combo.auc.original_name_file(tr)
                link_etp = combo.auc.document_link(tr)
                if pathlib.Path(''.join(original_name)).suffix in lst_exet \
                        or ''.join(filter(lambda x: x in link_etp, list(map(lambda y: y, lst_exet)))):
                    combo.auc.create_dir()
                    relative_path_f = combo.oazf.name_file_in_db_lot(response.url, lot, original_name)
                    name_on_server = combo.oazf.name_file_on_server_lot(response.url, lot, original_name)
                    load.request_to_download(url=link_etp, referer=response.url, original_name=name_on_server)
                lot.append({'original_name': original_name,
                            'link': relative_path_f,
                            'link_etp': u.parse_url(link_etp)})
        total_files = {'general': general, 'lot': lot}
        loader.add_value('files', total_files)
        loader.add_value('created_at', return_parse_date())
        return loader.load_item()

    # END__PARSE__OAZF__AUCTION_

    # PARSE__COMPETITION_
    def parse_competition(self, response):
        combo = ComboAuctionCompetition(response_=response)
        for i in range(len(combo.compet.full_text_lot_number)):
            loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
            loader.add_value('data_origin', data_origin_url)
            loader.add_value('trading_id', combo.auc.trading_id_auction(response.url))
            loader.add_value('trading_link', response.url)
            loader.add_value('trading_number', combo.auc.trading_number_auction(response.url))
            trade_link = ''.join(loader.get_collected_values('trading_link'))
            lot_number = get_lot_num_simple(''.join(combo.compet.full_text_lot_number[i]))
            if (trade_link, lot_number) not in self.previous_lots:
                loader.add_value('trading_type', check_trading_type(combo.compet.trading_form_compet))
                loader.add_value('trading_form', check_trading_form(combo.compet.trading_form_compet))
                loader.add_value('trading_org', combo.compet.trading_org_loc)
                loader.add_value('msg_number', combo.compet.msg_number(response.url))
                loader.add_value('case_number', combo.compet.case_number(response.url))
                loader.add_value('debtor_inn', combo.compet.debitor_inn(response.url))
                loader.add_value('arbit_manager', combo.compet.arbitr_manager(response.url))
                loader.add_value('arbit_manager_inn', combo.compet.arbitr_manag_inn(response.url))
                loader.add_value('arbit_manager_org', combo.compet.arbitr_org)
                status = response.meta['status']
                loader.add_value('status', status)
                loader.add_value('start_date_requests', combo.compet.start_date_request(response.url))
                loader.add_value('end_date_requests', combo.compet.end_date_request(response.url))
                loader.add_value('start_date_trading', combo.compet.start_date_trading(response.url))
                # lot info
                try:
                    short_name = ''.join(combo.compet.short_name_lots_compet[i])
                except:
                    short_name = None
                loader.add_value('lot_number', lot_number)
                loader.add_value('short_name', short_name)
                loader.add_value('property_information', combo.compet.property_info)
                try:
                    start_price = get_price(''.join(combo.compet.start_price_compet[i]).replace('-', ''). \
                                            replace(',', '.').replace('руб', ''))
                except:
                    start_price = None
                if start_price is None:
                    try:
                        start_price = get_price(''.join(combo.compet.start_price_compet_2[i]).replace('-', ''). \
                                                replace(',', '.'))
                    except:
                        start_price = None
                loader.add_value('start_price', start_price)

                # _GET_LINK_TO_TRADING_ORGANIZER_CONTACTS_
                link_to_org = combo.compet.get_trading_org_link
                # _GET_LINK_TO_DOCUMENTS_AUCTION_
                link_to_document = combo.auc.link_doc_page(response.url)
                referer_ = response.url
                yield Request(url=link_to_org, callback=self.parse_auction_organizer, dont_filter=True,
                              cb_kwargs={'loader': loader, 'referer': referer_,
                                         'link_to_document': link_to_document})

    async def parse_trade(self, response):
        offer = OfferParse(response_=response)
        combo = Combo(response)
        for lot in offer.count_lots():
            transfer = CrawlerBankruptItem()
            transfer['data_origin'] = data_origin_url
            transfer['trading_id'] = combo.trading_id
            transfer['trading_link'] = combo.trading_link
            transfer['trading_number'] = combo.trading_number
            transfer['trading_type'] = combo.trading_type
            transfer['trading_form'] = combo.trading_form
            transfer['trading_org'] = combo.trading_org
            transfer['trading_org_inn'] = combo.trading_org_inn
            transfer['trading_org_contacts'] = combo.trading_org_contacts
            transfer['msg_number'] = combo.msg_number
            transfer['case_number'] = combo.case_number
            transfer['debtor_inn'] = combo.debtor_inn
            address = offer.address
            region = None
            if address:
                region = Region.get_region(address)
            transfer['address'] = address
            transfer['region'] = region
            transfer['arbit_manager'] = combo.arbit_manager
            transfer['arbit_manager_inn'] = combo.arbit_manager_inn
            transfer['arbit_manager_org'] = combo.arbit_manager_org

            transfer['status'] = combo.get_status(lot)
            transfer['lot_id'] = combo.get_lot_id(lot)
            transfer['lot_link'] = combo.get_lot_link(lot)
            transfer['lot_number'] = combo.get_lot_number(lot)
            transfer['short_name'] = combo.get_short_name(lot)
            transfer['property_information'] = combo.get_property_information(lot)
            if transfer['trading_type'] in ['auction', 'competition']:
                transfer['start_date_requests'] = combo.get_start_date_requests(lot)
                transfer['end_date_requests'] = combo.get_end_date_requests(lot)
                transfer['start_date_trading'] = combo.get_start_date_trading(lot)
                transfer['end_date_trading'] = combo.get_end_date_trading(lot)
                transfer['start_price'] = combo.get_start_price(lot)
                transfer['step_price'] = combo.get_step_price(lot)
            else:
                transfer['periods'] = combo.periods(lot)
            yield Request(url=offer.link_doc_page(response.url), callback=self.documentation_offer,
                          cb_kwargs={'transfer': transfer,
                                     'referer': response.url, 'div_lot_html': lot,
                                     'trading_page_response': response}, dont_filter=True)

    def documentation_offer(self, response, transfer, referer, div_lot_html, trading_page_response):
        offer = OfferParse(response_=trading_page_response)
        lot = LotParse(response=response, lot=div_lot_html)
        offer_files = OfferParse(response_=response)
        general = offer_files.iteration_throughout_table_tr(offer.get_table_id(div_lot_html), response.url)
        loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
        lot_file = offer_files.iteration_throughout_lot_table_tr(offer.get_table_id(div_lot_html), referer)
        if lot_file is None:
            lot_file = list()
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_number', transfer['trading_number'])
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
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', transfer['status'])
        loader.add_value('lot_number', lot.get_lot_number())
        loader.add_value('short_name', lot.get_short_name())
        loader.add_value('property_information', lot.property_info())
        loader.add_value('start_date_requests', lot.start_date_request())
        loader.add_value('end_date_requests', lot.end_date_request())
        loader.add_value('start_date_trading', lot.start_date_trading())
        loader.add_value('end_date_trading', lot.end_date_trading())
        loader.add_value('start_price', lot.start_price())
        loader.add_value('periods', lot.get_all_periods())
        loader.add_value('created_at', return_parse_date())
        loader.add_value('files', {'general': general, 'lot': lot_file})
        yield loader.load_item()

    def parse_new_auction(self, response):
        offer = OfferParse(response_=response)
        for lot in offer.count_lots():
            transfer = CrawlerBankruptItem()
            transfer['data_origin'] = offer.data_origin_offer
            transfer['trading_id'] = offer.trading_id(response.url)
            transfer['trading_link'] = response.url
            transfer['trading_number'] = offer.trading_number
            transfer['trading_type'] = 'auction'
            transfer['trading_form'] = 'open'
            transfer['trading_org'] = offer.trading_org
            transfer['trading_org_inn'] = offer.trading_org_inn
            transfer['trading_org_contacts'] = {'email': offer.trading_org_email,
                                                'phone': offer.get_phone_org}
            transfer['msg_number'] = offer.msg_number(response.url)
            transfer['case_number'] = offer.case_number(response.url)
            transfer['debtor_inn'] = offer.debitor_inn
            address = offer.address
            region = None
            if address:
                region = Region.get_region(address)
            transfer['address'] = address
            transfer['region'] = region
            transfer['arbit_manager'] = offer.arbitr_name
            transfer['arbit_manager_inn'] = offer.arbitr_inn
            transfer['arbit_manager_org'] = offer.arbitr_org
            transfer['status'] = response.meta['status']
            yield Request(url=offer.link_doc_page(response.url), callback=self.documentation_auction,
                          cb_kwargs={'transfer': transfer,
                                     'referer': response.url, 'div_lot_html': lot,
                                     'trading_page_response': response},
                          dont_filter=True)

    def documentation_auction(self, response, transfer, referer, div_lot_html, trading_page_response):
        offer = OfferParse(response_=trading_page_response)
        offer_files = OfferParse(response_=response)
        lot = LotParse(response=response, lot=div_lot_html)
        general = offer_files.iteration_throughout_table_tr(offer.get_table_id(div_lot_html), response.url)
        loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
        lot_file = offer_files.iteration_throughout_lot_table_tr(offer.get_table_id(div_lot_html), referer)
        if lot_file is None:
            lot_file = list()
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_number', transfer['trading_number'])
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
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', transfer['status'])
        loader.add_value('lot_number', lot.get_lot_number())
        loader.add_value('short_name', lot.get_short_name())
        loader.add_value('property_information', lot.property_info())
        loader.add_value('start_date_requests', lot.start_req_auc())
        loader.add_value('end_date_requests', lot.end_req_auc())
        loader.add_value('start_date_trading', lot.start_trading_auc())
        loader.add_value('end_date_trading', lot.end_trading_auc())
        loader.add_value('start_price', lot.start_price_auc())
        loader.add_value('step_price', lot.step_price_auc())
        loader.add_value('created_at', return_parse_date())
        loader.add_value('files', {'general': general, 'lot': lot_file})
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
