# -*- coding: utf-8 -*-
import copy

from bs4 import BeautifulSoup as BS
from scrapy import FormRequest
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest, SlotPolicy, SplashFormRequest
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from ..items import CrawlerFedresursItem, DebitorItemLoader
from ..locators.debitor_locator import DebitrLocator
from ..manage_spiders.app import Combo
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..utils.config import *
from ..utils.connect_for_change_status import SetValueDb
from ..utils.data_for_requests import script_lua, script_lua_category
from ..utils.post_data_debitor import post_debitor_company, post_debitor_follow_person, post_debitor_person, \
    header_page_deb
from ..utils.read_debitor_data import ReadDebitr
from ..utils.work_with_text_and_number import return_complex_cookies, cookie_parser, return_complex_cookies_person
from ..utils.working_with_time import return_parse_date
from ..utils.working_with_url import UrlConfig
import time


class FedresDebitorSpider(CrawlSpider):
    name = 'fedres_debitor'
    # allowed_domains = ['bankrot.fedresurs.ru']
    # start_urls = ['https://bankrot.fedresurs.ru/']

    custom_settings = {
        'SPLASH_URL': SPLASH_URL_DEBITOR,
        'DOWNLOADER_MIDDLEWARES': {
            'crawler_fedresurs.middlewares.UserAgentMiddleware': 500,
            'scrapy_splash.SplashCookiesMiddleware': 723,
            'scrapy_splash.SplashMiddleware': 725,
            'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 810,
            'rotating_proxies.middlewares.RotatingProxyMiddleware': 610,
            'rotating_proxies.middlewares.BanDetectionMiddleware': 620,
        },
        'ITEM_PIPELINES': {
            'crawler_fedresurs.pipelines.CrawlerFedresursPipeline': 300,
            'crawler_fedresurs.pipelines.DbConnectDebitor': 350,
            'crawler_fedresurs.pipelines.ManageTaskTableDebitor': 370,
        }
    }

    def __init__(self, *args, **kwargs):
        super(FedresDebitorSpider, self).__init__(*args, **kwargs)
        self.url_spider = UrlConfig()
        self.debitr = ReadDebitr()
        self.ch_value = SetValueDb()

    def start_requests(self):

        debitor_inn = self.debitr.get_debitr_inn()
        os.chdir(DIR_DEBITR)
        time.sleep(0.5)
        os.system('rm post_data_debit*')
        os.chdir(DIR_PROJECT)
        time.sleep(0.5)
        yield SplashRequest(self.url_spider.parse_url(start_link), self.parse_main_page, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=DEFAULT_REQUESTS_HEADERS,
                            session_id=1,
                            errback=self.errback_httpbin, cb_kwargs={'deb_inn': debitor_inn})

    async def parse_main_page(self, response, deb_inn):
        """after receiving cookies go to DEBITOR page"""
        yield SplashRequest(self.url_spider.parse_url(debitr_link), self.page_with_debitor_form_company,
                            endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua_category},
                            slot_policy=SlotPolicy.PER_DOMAIN,
                            session_id=1,
                            errback=self.errback_httpbin, cb_kwargs={'deb_inn': deb_inn})

    async def page_with_debitor_form_company(self, response, deb_inn):
        """now on page with debitor(company) form.  Sorted person inn and follow to form...
            if company (10 numbers of inn than follow to serp of companies.
        """
        combo = Combo(response_=response)
        post_debitor_company['__EVENTTARGET'] = combo.arbitr.get_EVENTTARGET
        post_debitor_company['__EVENTARGUMENT'] = combo.arbitr.get_EVENTARGUMENT
        post_debitor_company['__VIEWSTATE'] = combo.arbitr.get_VIEWSTATE
        post_debitor_company['__VIEWSTATEGENERATOR'] = combo.arbitr.get_VIEWSTATEGENERATOR
        post_debitor_company['__PREVIOUSPAGE'] = combo.arbitr.get_PREVIOUSPAGE
        if deb_inn is not None:
            for i in deb_inn:
                if i is not None:
                    self.ch_value.change_status_organizer(DEBITR, i, 'failed')
                if i is not None and len(i) == 10:
                    post_debitor_company['ctl00$cphBody$OrganizationCode1$CodeTextBox'] = ''.join(i).strip()
                    yield SplashFormRequest(response.url, callback=self.parse_serp_company,
                                            formdata=post_debitor_company,
                                            endpoint='execute',
                                            cache_args=['lua_source'],
                                            method='POST',
                                            args={'lua_source': script_lua_category},
                                            slot_policy=SlotPolicy.PER_DOMAIN,
                                            # session_id=1,
                                            errback=self.errback_httpbin, dont_filter=True,
                                            cb_kwargs={'origin_inn': i})
                elif i is not None and len(i) == 12:
                    post_debitor_follow_person['__EVENTTARGET'] = combo.arbitr.get_EVENTTARGET
                    post_debitor_follow_person['__EVENTARGUMENT'] = combo.arbitr.get_EVENTARGUMENT
                    post_debitor_follow_person['__VIEWSTATE'] = combo.arbitr.get_VIEWSTATE
                    post_debitor_follow_person['__VIEWSTATEGENERATOR'] = combo.arbitr.get_VIEWSTATEGENERATOR
                    post_debitor_follow_person['__PREVIOUSPAGE'] = combo.arbitr.get_PREVIOUSPAGE
                    yield SplashFormRequest(response.url, callback=self.person_page_form,
                                            formdata=post_debitor_follow_person,
                                            endpoint='execute',
                                            cache_args=['lua_source'],
                                            method='POST',
                                            args={'lua_source': script_lua_category},
                                            slot_policy=SlotPolicy.PER_DOMAIN,
                                            session_id=1,
                                            errback=self.errback_httpbin, dont_filter=True,
                                            cb_kwargs={'origin_inn': i,
                                                       'post_deb': post_debitor_follow_person})

    async def parse_serp_company(self, response, origin_inn):
        import pprint
        """parse list of links(as searching for inn link must be one) company debitr"""
        soup = BS(str(response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        links = soup.find_all(href=re.compile('OrganizationCard\.aspx'))
        cookies = response.data['cookies']
        count_links = len(links)
        _headers = copy.deepcopy(header_page_deb)
        _headers['user-agent'] = headers_brow['User-Agent']
        _headers['referer'] = response.url
        _cookies = return_complex_cookies(cookies, origin_inn)
        for link in links:
            link = self.url_spider.url_join(start_link, link.get('href'))
            _headers[':path'] = '/' + link.split('/')[-1]
            yield FormRequest(link, method='POST',
                              callback=self.company_card_parse,
                              cookies=cookie_parser(_cookies),
                              headers=_headers, errback=self.errback_httpbin,
                              cb_kwargs={'origin_inn': origin_inn, 'count_links': count_links})
            # yield SplashRequest(self.url_spider.url_join(start_link, link.get('href')),
            #                     callback=self.company_card_parse,
            #                     endpoint='execute',
            #                     cache_args=['lua_source'], args={'lua_source': script_lua_category},
            #                     slot_policy=SlotPolicy.PER_DOMAIN,
            #                     session_id=1, dont_filter=True,
            #                     errback=self.errback_httpbin,
            #                     cb_kwargs={'origin_inn': origin_inn, 'count_links': count_links})

    async def company_card_parse(self, response, origin_inn, count_links):
        """parse info about debitor - company"""
        locator = DebitrLocator
        loader = DebitorItemLoader(CrawlerFedresursItem(), response=response)
        loader.add_value('links_count', count_links)
        loader.add_value('item_type', DEBITR)
        loader.add_value('item_transfer', origin_inn)
        soup = BS(str(response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        table = soup.find('table', class_='au')
        if table:
            for row in table.find_all('tr'):
                get_id = row.get('id')
                if get_id == locator.full_name_loc:
                    loader.add_value('full_name', row.findAll('td')[1].get_text().strip())
                if get_id == locator.category_loc:
                    loader.add_value('category', row.findAll('td')[1].get_text().strip())
                if get_id == locator.region_loc:
                    loader.add_value('region', row.findAll('td')[1].get_text().strip())
                if get_id == locator.address_loc:
                    loader.add_value('address', row.findAll('td')[1].get_text().strip())
                if get_id == locator.inn_loc:
                    loader.add_value('inn', row.findAll('td')[1].get_text().strip())
                if get_id == locator.ogrn_loc:
                    loader.add_value('ogrn', row.findAll('td')[1].get_text().strip())
            loader.add_value('created_at', return_parse_date())
            loader.add_value('link', response.url)
        yield loader.load_item()

    async def person_page_form(self, response, origin_inn, post_deb):
        """make post request from debitor person page"""
        cookies = response.data['cookies']
        post_debitor_person['__EVENTTARGET'] = post_deb['__EVENTTARGET']
        post_debitor_person['__EVENTARGUMENT'] = post_deb['__EVENTARGUMENT']
        post_debitor_person['__VIEWSTATE'] = post_deb['__VIEWSTATE']
        post_debitor_person['__VIEWSTATEGENERATOR'] = post_deb['__VIEWSTATEGENERATOR']
        post_debitor_person['__PREVIOUSPAGE'] = post_deb['__PREVIOUSPAGE']
        post_debitor_person['ctl00$cphBody$PersonCode1$CodeTextBox'] = ''.join(origin_inn).strip()
        yield SplashFormRequest(response.url, callback=self.parse_serp_deb_person,
                                formdata=post_debitor_person,
                                endpoint='execute',
                                cache_args=['lua_source'],
                                method='POST',
                                args={'lua_source': script_lua_category},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                session_id=1,
                                errback=self.errback_httpbin, dont_filter=True,
                                cb_kwargs={'origin_inn': origin_inn,
                                           })

    async def parse_serp_deb_person(self, response, origin_inn):
        """parse list of links(as searching for inn link must be one) person debitr"""
        soup = BS(str(response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        links = soup.find_all(href=re.compile(r'PrivatePersonCard\.aspx'))
        cookies = response.data['cookies']
        count_links = len(links)
        _headers = copy.deepcopy(header_page_deb)
        _headers['user-agent'] = headers_brow['User-Agent']
        _headers['referer'] = response.url
        _cookies = return_complex_cookies_person(cookies, origin_inn)
        for link in links:
            link = self.url_spider.url_join(start_link, link.get('href'))
            _headers[':path'] = '/' + link.split('/')[-1]
            yield FormRequest(link, method='POST',
                              callback=self.person_card_parse,
                              cookies=cookie_parser(_cookies),
                              headers=_headers, errback=self.errback_httpbin,
                              cb_kwargs={'origin_inn': origin_inn, 'count_links': count_links})
        # for link in links:
        #     yield SplashRequest(self.url_spider.url_join(start_link, link.get('href')),
        #                         callback=self.person_card_parse,
        #                         endpoint='execute',
        #                         cache_args=['lua_source'], args={'lua_source': script_lua_category},
        #                         slot_policy=SlotPolicy.PER_DOMAIN,
        #                         session_id=1, dont_filter=True,
        #                         errback=self.errback_httpbin,
        #                         cb_kwargs={'count_links': count_links, 'origin_inn': origin_inn})

    async def person_card_parse(self, response, count_links, origin_inn):
        """parse personal info debitor(person)"""
        combo = Combo(response_=response)
        locator = DebitrLocator()
        loader = DebitorItemLoader(CrawlerFedresursItem(), response=response)
        loader.add_value('links_count', count_links)
        loader.add_value('item_type', DEBITR)
        loader.add_value('item_transfer', origin_inn)
        soup = BS(str(response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        table = soup.find('table', id='ctl00_cphBody_tblSroCardInfo')
        lastname, firstname, midname = '', '', ''
        if table is None:
            table = soup.find('table', class_='au')
        if table:
            for row in table.find_all('tr'):
                get_id = row.get('id')
                if get_id == locator.last_name_loc:
                    lastname = row.findAll('td')[1].get_text().strip()
                if get_id == locator.first_name_loc:
                    firstname = row.findAll('td')[1].get_text().strip()
                if get_id == locator.middle_name_loc:
                    midname = row.findAll('td')[1].get_text().strip()
                if get_id == locator.category_loc:
                    loader.add_value('category', row.findAll('td')[1].get_text().strip())
                if get_id == locator.region_loc:
                    loader.add_value('region', row.findAll('td')[1].get_text().strip())
                if get_id == locator.address_loc:
                    loader.add_value('address', row.findAll('td')[1].get_text().strip())
                if get_id == locator.inn_loc:
                    loader.add_value('inn', row.findAll('td')[1].get_text().strip())
                if get_id == locator.ogrn_loc:
                    loader.add_value('ogrn', row.findAll('td')[1].get_text().strip())
            loader.add_value('created_at', return_parse_date())
        loader.add_value('full_name', combo.arbitr.full_name_return(lastname, firstname, midname))
        loader.add_value('link', response.url)
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
