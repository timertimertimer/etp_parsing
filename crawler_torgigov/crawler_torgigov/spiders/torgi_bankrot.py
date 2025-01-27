import copy
import logging
from abc import ABC
from random import choice

import aiohttp
from aiohttp_socks import ProxyConnector
from icecream import ic
from scrapy import Request, FormRequest
from scrapy.http.cookies import CookieJar
from scrapy.spiders import Spider

from crawler_torgigov.utils.db import *
from crawler_torgigov.utils.db_check_download import *
from ..items import CrawlerTorgigovItem, CrawlerTorgigovItemLoader
from ..manage_spider.aiohttp_manage import *
from ..manage_spider.aiohttp_manage import ChangeLink
from ..manage_spider.app import Combo
from ..utils.config import bankrot_link
from ..utils.download import agent_list, socks_list
from ..utils.global_functions import GlobalFeatures
from ..utils.headers import headers, headers_for_lot_page, short_headers
from ..utils.work_with_text_and_number import cookie_parser
from ..utils.working_with_time import return_parse_date

logger = logging.getLogger(__name__)


class TorgiBankrotSpider(Spider, ABC):
    name = 'torgi_bankrot'
    start_url = 'https://gosbar.gosuslugi.ru/sites/torgi.gov.ru'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
        'LOG_LEVEL': 'INFO',
        'DOWNLOADER_MIDDLEWARES': {
            'crawler_torgigov.middlewares.CrawlerTorgigovDownloaderMiddleware': 543,
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        },
        'ITEM_PIPELINES': {
            'crawler_torgigov.pipelines.CrawlerTorgigovPipeline': 300,
            'crawler_torgigov.pipelines.TorgiGovConnect': 350,
        }

    }

    def __init__(self, section_of_trade='', date_from='', date_to=''):
        super(TorgiBankrotSpider, self).__init__()
        self.sec = section_of_trade
        self.date_from = date_from
        self.date_to = date_to
        self.glo = GlobalFeatures(self.sec, self.date_from, self.date_to)

    def start_requests(self):
        yield Request(self.start_url, self.parsemain)

    def parsemain(self, response):
        """ from main page do request to bankrot section """
        yield Request(url=bankrot_link['torgi_bankrot'], callback=self.parse_bankrot_section, headers=headers)

    def parse_bankrot_section(self, response):
        """ do request to section according spider arguments """
        url = self.glo.choose_parse_section()
        headers['Referer'] = response.url

        yield Request(url=url, callback=self.extended_form, headers=headers, cb_kwargs={'url_of_section': url})

    def extended_form(self, response, url_of_section):
        """ do request to extended form """
        combo = Combo(response_=response)
        _id = combo.finished.get_id_form()
        headers['Referer'] = response.url
        headers['User-Agent'] = choice(agent_list)
        headers['Wicket-Ajax'] = 'true'
        headers['Wicket-FocusedElementId'] = _id
        search_button_id = combo.finished.get_search_button()
        link_to_extended_form = combo.finished.link_for_extend_form(url_of_section)
        hiden_id = combo.finished.get_hidden_input()
        # for open extended form
        param_extended_form = self.glo.param_data_extended_form()
        param_extended_form[hiden_id] = ''
        search_button_link = combo.finished.get_search_button_link(url_of_section)
        yield FormRequest(link_to_extended_form, callback=self.another_request_activate_form_org,
                          formdata=param_extended_form,
                          headers=headers, method='POST',
                          cb_kwargs={'hiden_id': hiden_id, 'search_button_id': search_button_id,
                                     'url_of_section': url_of_section, 'header': headers,
                                     'search_button_link': search_button_link})

    async def another_request_activate_form_org(self, response, hiden_id, search_button_id, url_of_section, header,
                                                search_button_link):
        """ do one more requests to activate organizer form(field) (ajax)"""
        combo = Combo(response_=response)
        country_id = combo.finished.get_id_field_counrty()
        # delete due it's not needed
        del header['Wicket-FocusedElementId']
        url = combo.finished.get_organizer_link(url_of_section, response.text)
        url_field_country = combo.finished.get_country_link(url_of_section, response.text)
        yield Request(url, callback=self.another_request_activate_country, headers=header,
                      cb_kwargs={'url_of_section': url_of_section, 'header': header, 'hiden_id': hiden_id,
                                 'search_button_id': search_button_id,
                                 'country_id': country_id,
                                 'country_link': url_field_country,
                                 'search_button_link': search_button_link})

    async def another_request_activate_country(self, response, url_of_section, header, hiden_id, search_button_id,
                                               country_id, country_link, search_button_link):
        """ do one more requests to activate country field (ajax)} """
        header['Wicket-FocusedElementId'] = country_id
        yield FormRequest(country_link, callback=self.form_data_country,
                          formdata={'extended:country': '185', '': ''},
                          headers=header, method='POST',
                          cb_kwargs={'url_of_section': url_of_section, 'header': header,
                                     'search_button_id': search_button_id, 'hiden_id': hiden_id,
                                     'search_button_link': search_button_link}, dont_filter=True)

    async def form_data_country(self, response, url_of_section, header, search_button_id, hiden_id, search_button_link):
        """ request to activate country field """
        param = self.glo.param_data_for_parsing()
        param[hiden_id] = ''
        if self.sec == 'active':
            param['extended:bidNumberExtended:publishDateFrom'] = self.glo.date_from_func()
            param['extended:bidNumberExtended:publishDateTo'] = self.glo.date_to_func()
        elif self.sec == 'archived':
            param['extended:bidNumberExtended:expireDateFrom'] = self.glo.date_from_func()
            param['extended:bidNumberExtended:expireDateTo'] = self.glo.date_to_func()
        else:
            param['extended:bidNumberExtended:expireDateFrom'] = self.glo.date_from_func()
            param['extended:bidNumberExtended:expireDateTo'] = self.glo.date_to_func()
        header['Referer'] = url_of_section
        header['Wicket-FocusedElementId'] = search_button_id
        url = search_button_link
        yield FormRequest(url, callback=self.output_search, formdata=param, headers=header,
                          cb_kwargs={'url_of_section': url_of_section, 'current_page': 1, 'header': header},
                          dont_filter=True)

    async def output_search(self, response, url_of_section, current_page, header):
        """ get lots and find pagination """
        combo = Combo(response_=response)
        cookie_byte = response.request.headers['Cookie']
        cookie_str = cookie_byte.decode('utf-8')
        next_page = combo.finished.get_link_next(url_of_section)
        if links_to_lots := combo.finished.get_links_to_lots():
            for link in links_to_lots:
                yield Request(url=link, callback=self.parse_lot, headers=headers_for_lot_page,
                              cookies=cookie_parser(cookie_str),
                              cb_kwargs={'header': header, 'general_link': link, 'cookie_str': cookie_str,
                                         'attemp': 1}, dont_filter=True)

        if next_page:
            current_page += 1
            header['Wicket-FocusedElementId'] = combo.finished.get_id_link_next()
            yield Request(next_page, callback=self.output_search, headers=header,
                          cb_kwargs={'url_of_section': url_of_section, 'current_page': current_page,
                                     'header': header})

    async def parse_lot(self, response, header, general_link, cookie_str, attemp):
        """ parse lot page """
        combo = Combo(response_=response)
        category = combo.lot.get_category()
        if ('Акции' or 'Доля ООО') not in category['classification']:
            trading_type = combo.lot.get_trading_type()
            loader = CrawlerTorgigovItemLoader(CrawlerTorgigovItem(), response=response)
            loader.add_value('data_origin', combo.lot.get_data_origin())
            loader.add_value('trading_id', combo.lot.get_trading_id())
            loader.add_value('trading_link', combo.lot.get_trading_link())
            loader.add_value('trading_number', combo.lot.get_trading_number())
            loader.add_value('trading_type', trading_type)
            loader.add_value('trading_form', combo.lot.get_trading_form)
            status = 'active'
            loader.add_value('status', status)
            loader.add_value('category', category)
            loader.add_value('address', combo.lot.get_address())
            loader.add_value('detailed_address', combo.lot.get_detailed_address())
            loader.add_value('encumbrance', combo.lot.get_encumbrance())
            loader.add_value('description_encumbrance', combo.lot.get_description_encumbrance())
            loader.add_value('lot_number', combo.lot.get_lot_number())
            loader.add_value('short_name', combo.lot.get_short_name())
            loader.add_value('lot_info', None)
            loader.add_value('property_information', combo.lot.property_information(general_link))
            # loader.add_value('start_date_trading', None)
            # loader.add_value('end_date_trading', None)
            loader.add_value('quantity', None)
            loader.add_value('unit', None)
            loader.add_value('deposit', combo.lot.get_deposit())
            loader.add_value('start_price', combo.lot.get_start_price(trading_type))
            loader.add_value('min_price', combo.lot.get_min_price(general_link))
            loader.add_value('step_price', combo.lot.get_step_price(general_link))
            loader.add_value('periods', None)
            loader.add_value('files', None)
            loader.add_value('created_at', return_parse_date())
            trading_page = combo.lot.get_link_to_trading_page()
            header['Wicket-FocusedElementId'] = combo.lot.get_id_trading_page()
            header['Wicket-Ajax'] = 'true'
            header['Referer'] = general_link
            # if start date request is absent on general get from lot page
            start_request_additional = combo.lot.start_date_request_extra(general_link)
            yield Request(url=trading_page, callback=self.parse_general_page, headers=header,
                          cookies=cookie_parser(cookie_str),
                          meta={'dont_redirect': True, "handle_httpstatus_list": [302, 307, 301]},
                          cb_kwargs={'loader': loader, 'header': header, 'general_link': general_link,
                                     'cookie_str': cookie_str, 'attemp': attemp, 'start_req': start_request_additional,
                                     'trading_type': trading_type},
                          dont_filter=True)

    async def parse_general_page(self, response, loader, header, general_link, cookie_str, attemp, start_req, trading_type):
        """ parse general page """
        combo = Combo(response_=response)
        response_byte_dict = response.headers
        ajax_key = response_byte_dict.get('Ajax-Location', None)
        if ajax_key is None:
            loader.add_value('trading_org', combo.gen.get_organizer_name(general_link))
            loader.add_value('trading_org_contacts', combo.gen.get_organizer_contacts(general_link))
            loader.add_value('index', combo.gen.get_address_index(general_link))
            loader.add_value('start_date_requests', combo.gen.start_date_request_bankrot(general_link))
            loader.add_value('end_date_requests', combo.gen.end_date_request_bankrot(general_link))
            loader.add_value('start_date_trading', combo.gen.start_date_trading_bankrot(general_link, trading_type))
            start_date_request_check = loader.get_collected_values('start_date_requests')
            header['Wicket-FocusedElementId'] = combo.gen.get_id_download_page(general_link)
            document_page = combo.gen.get_link_to_document_page(general_link)
            cookieJar = response.meta.setdefault('cookie_jar', CookieJar())
            cookieJar.extract_cookies(response, response.request)
            request = Request(url=document_page, callback=self.parse_document_page, headers=header,
                              cb_kwargs={'loader': loader, 'header': header, 'general_link': general_link,
                                         'attemp': attemp,
                                         'cookie_str': cookie_str, 'start_req': start_req
                                         },
                              dont_filter=True,
                              meta={'cookie_jar': cookieJar})
            cookieJar.add_cookie_header(request)
            yield request
        else:
            attemp += 1
            header['Referer'] = 'https://torgi.gov.ru/index.html'
            if attemp < 4:
                yield Request(url=general_link, callback=self.parse_lot, headers=headers_for_lot_page,
                              cookies=cookie_parser(cookie_str),
                              cb_kwargs={'header': header, 'general_link': general_link, 'cookie_str': cookie_str,
                                         'attemp': attemp},
                              dont_filter=True)

    # _____________________DOCUMENTS________________________
    async def parse_document_page(self, response, loader, header, general_link, attemp, cookie_str, start_req):
        """ parse page with documents """
        response_byte_dict = response.headers
        ajax_key = response_byte_dict.get('Ajax-Location', None)
        if ajax_key is not None:
            attemp += 1
            header['Referer'] = 'https://torgi.gov.ru/index.html'
            if attemp < 5:
                yield Request(url=general_link, callback=self.parse_lot, headers=headers_for_lot_page,
                              cookies=cookie_parser(cookie_str),
                              cb_kwargs={'header': header, 'general_link': general_link, 'cookie_str': cookie_str,
                                         'attemp': attemp},
                              dont_filter=True)
        else:
            FILES_TO_DOWNLOAD = list()
            FILES_REDIRECT = list()
            general = []
            id_lot = ''.join(loader.get_collected_values('trading_id'))
            trading_link = ''.join(loader.get_collected_values('trading_link'))
            cookie_byte = response.request.headers['Cookie']
            cookie_aio = cookie_byte.decode('utf-8')
            header_aio = copy.deepcopy(header)
            # ic(ast.literal_eval(cookie_byte.decode("utf-8")))
            combo = Combo(response_=response)
            header['Referer'] = response.url
            # check if lot with current id exists in db. if yes, compeare files if match return complete dict with files
            get_previous_files = loop.run_until_complete(
                async_check_download(loop, trading_id=id_lot))
            if files_tuple := combo.doc.return_file_data(general_link):
                for f in files_tuple:
                    if re.match(r'https://torgi.gov.ru/resources/.+', f[0]):
                        # f[0] - link; f[1] - file name
                        FILES_TO_DOWNLOAD.append((f[0], f[1]))
                    elif re.match(r'https://torgi.gov.ru/\?wicket', f[0]):
                        FILES_REDIRECT.append((f[0], f[1]))
            else:
                loader.add_value('files', {'general': general, 'lot': []})
                start_date_request_check = loader.get_collected_values('start_date_requests')
                if len(start_date_request_check) == 0:
                    loader.add_value('start_date_requests', start_req)
                yield loader.load_item()
            if (get_previous_files is None) or (len(get_previous_files['general']) == 0):
                if len(FILES_REDIRECT) == 0:
                    general = combo.doc_gen.download_trade(FILES_TO_DOWNLOAD, self.name, id_lot, general_link)
                    loader.add_value('files', {'general': general, 'lot': []})
                    FILES_TO_DOWNLOAD.clear()
                    start_date_request_check = loader.get_collected_values('start_date_requests')
                    if len(start_date_request_check) == 0:
                        loader.add_value('start_date_requests', start_req)
                    yield loader.load_item()
                elif len(FILES_REDIRECT) > 0:
                    FILES_TO_DOWNLOAD = await self.go_to_page_view(FILES_TO_DOWNLOAD=FILES_TO_DOWNLOAD,
                                                                   FILES_REDIRECT=FILES_REDIRECT,
                                                                   general_link=general_link,
                                                                   response=response, header_aio=header_aio,
                                                                   trading_link=trading_link,
                                                                   cookie_aio=cookie_aio)
                    general = combo.doc_gen.download_trade(FILES_TO_DOWNLOAD, self.name, id_lot, general_link)
                    loader.add_value('files', {'general': general, 'lot': []})
                    FILES_TO_DOWNLOAD.clear()
                    FILES_REDIRECT.clear()
                    start_date_request_check = loader.get_collected_values('start_date_requests')
                    if len(start_date_request_check) == 0:
                        loader.add_value('start_date_requests', start_req)
                    yield loader.load_item()
            elif (get_previous_files is not None) and (len(get_previous_files['general']) > 0):
                FILES_TO_DOWNLOAD.extend(FILES_REDIRECT)
                if isinstance(get_previous_files, dict):
                    compare_links = combo.doc.compare_links_to_download(dct=get_previous_files,
                                                                        lst=FILES_TO_DOWNLOAD)
                    # compere files from db and list with files(names) from document page. If min 25% is equal than copy value from db
                    if compare_links > 0.25:
                        general = get_previous_files
                        loader.add_value('files', general)
                        FILES_TO_DOWNLOAD.clear()
                        start_date_request_check = loader.get_collected_values('start_date_requests')
                        if len(start_date_request_check) == 0:
                            loader.add_value('start_date_requests', start_req)
                        yield loader.load_item()
                    else:
                        FILES_TO_DOWNLOAD = await self.go_to_page_view(FILES_TO_DOWNLOAD=FILES_TO_DOWNLOAD,
                                                                       FILES_REDIRECT=FILES_REDIRECT,
                                                                       general_link=general_link,
                                                                       response=response, header_aio=header_aio,
                                                                       trading_link=trading_link,
                                                                       cookie_aio=cookie_aio)
                        general = combo.doc_gen.download_trade(FILES_TO_DOWNLOAD, self.name, id_lot, general_link)
                        loader.add_value('files', {'general': general, 'lot': []})
                        FILES_TO_DOWNLOAD.clear()
                        FILES_REDIRECT.clear()
                        start_date_request_check = loader.get_collected_values('start_date_requests')
                        if len(start_date_request_check) == 0:
                            loader.add_value('start_date_requests', start_req)
                        yield loader.load_item()
                        logger.error(f'{general_link} :: ERROR WITH COMPARE FILES MAIN SPIDER')

    async def parse_with_asyncio(self, response, link, header, main_link, cookie, name_file):
        try:
            connector = ProxyConnector.from_url(f'socks5://{choice(socks_list)}')
            timeout = aiohttp.ClientTimeout(total=10)
            header['Cookie'] = cookie
            url_ = None
            transit_list = list()
            async with aiohttp.ClientSession(headers=header, connector=connector, timeout=timeout) as session:
                async with session.get(url=link, allow_redirects=False) as redirect_url:
                    change = ChangeLink()
                    res_text = await redirect_url.text()
                    # get redirect link
                    url_ = change.return_link(res_text=res_text)
                    link_to_view = re.sub(r'^https', 'http', str(url_))
                    # Location1 = str(redirect_url).split("Location': \'")[1].split("\'")[0]
                    new_header = copy.deepcopy(short_headers)
                    new_header['Pragma'] = 'no-cache'
                    new_header['Sec-Fetch-Dest'] = 'document'
                    new_header['Sec-Fetch-Mode'] = 'navigate'
                    new_header['Sec-Fetch-Site:'] = 'cross-site'
                    session.headers.update(new_header)
                    # link_to_view = change.change_sequence_of_query(link_to_view)
                    async with session.get(url=link_to_view, allow_redirects=False) as redirect_301:
                        Location = str(redirect_301).split("Location': \'")[1].split("\'")[0]
                        link_download = await self.request_to_doc_page(connector, url_=Location, time_out=timeout)
                        transit_list.append((link_download, name_file))
                        return transit_list

                    return list()
        except:
            # logger.error(f'{response.url} :{e}: ERROR async parse documents page', exc_info=True)
            return None

    async def request_to_doc_page(self, connector_, url_, time_out):
        async with aiohttp.ClientSession(headers=short_headers, connector=connector_, timeout=time_out) as session:
            async with session.request(url=url_, method='GET') as final:
                change = ChangeLink()
                res_text_ = await final.text()
                link = change.get_link_to_download(res_text_)
                return link

    async def go_to_page_view(self, FILES_REDIRECT, FILES_TO_DOWNLOAD, general_link, response, header_aio,
                              trading_link, cookie_aio):
        """ go to page with pre-view document  """
        for f in range(len(FILES_REDIRECT)):
            get_async_files = None
            link_ = FILES_REDIRECT.pop()
            # loop if error
            stop_loop = 50
            while stop_loop > 0 and get_async_files is None:
                if stop_loop == 10:
                    logger.error(f'{general_link} :: ERROR DURING ASYNC REQUEST TO FILE')
                stop_loop -= 1
                get_async_files = asyncio.run(self.parse_with_asyncio(response=response, link=link_[0],
                                                                      header=header_aio,
                                                                      main_link=trading_link,
                                                                      cookie=cookie_aio,
                                                                      name_file=link_[1]))
                if get_async_files:
                    FILES_TO_DOWNLOAD.extend(get_async_files)
        return FILES_TO_DOWNLOAD
