# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest, SlotPolicy, SplashFormRequest
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from ..items import CrawlerFedresursItem, ArbitrItem
from ..locators.arbitr_locator import ArbitrLocators
from ..manage_spiders.app import Combo
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..utils.config import *
from ..utils.connect_for_change_status import SetValueDb
from ..utils.data_for_requests import script_lua, script_lua_category
from ..utils.post_data_arbitr import post_arbitr
from ..utils.read_arbitr_data import ReadArbitr
from ..utils.work_with_text_and_number import return_clean_name
from ..utils.working_with_time import return_parse_date
from ..utils.working_with_url import UrlConfig
import time

class FedresArbitorSpider(CrawlSpider):
    name = 'fedres_arbitor'
    # allowed_domains = ['bankrot.fedresurs.ru']
    # start_urls = ['https://bankrot.fedresurs.ru/']

    custom_settings = {
        'SPLASH_URL': SPLASH_URL_ARBITOR,
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
            'crawler_fedresurs.pipelines.DbConnectArbitr': 350,
            'crawler_fedresurs.pipelines.ManageTaskTableArbitr': 370,
        }

    }

    def __init__(self, *args, **kwargs):
        super(FedresArbitorSpider, self).__init__(*args, **kwargs)
        self.url_spider = UrlConfig()
        self.arbitr = ReadArbitr()
        self.ch_value = SetValueDb()

    def start_requests(self):
        """befor yield first request -> get data for query from files and then delete files"""
        arbitr_names = self.arbitr.get_arbitr_names()
        # ---- after get all data from file delete them and back to project dir
        os.chdir(DIR_ARBITOR)
        time.sleep(0.5)
        os.system('rm post_data_arbit*.json')
        os.chdir(DIR_PROJECT)
        time.sleep(0.5)
        yield SplashRequest(self.url_spider.parse_url(start_link), self.parse_main_page, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=DEFAULT_REQUESTS_HEADERS,
                            session_id=1,
                            errback=self.errback_httpbin, cb_kwargs={'arbitr_names': arbitr_names})

    async def parse_main_page(self, response, arbitr_names):
        """after receiving cookies go to Arbitr page"""
        yield SplashRequest(self.url_spider.parse_url(arbitr_link), self.page_with_arbitr_form,
                            endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua_category},
                            slot_policy=SlotPolicy.PER_DOMAIN,
                            session_id=1,
                            errback=self.errback_httpbin, cb_kwargs={'arbitr_names': arbitr_names})

    async def page_with_arbitr_form(self, response, arbitr_names):
        """get data for post requests"""
        combo = Combo(response_=response)
        for a in arbitr_names:
            self.ch_value.change_status_organizer(ARBITR_NAME, a, 'failed')
            name = ''.join(return_clean_name(a)).split(' ')
            if len(name) == 2:
                name.append(' ')
            if len(name) >= 3:
                attemp = 0
                post_arbitr['__EVENTTARGET'] = combo.arbitr.get_EVENTTARGET
                post_arbitr['__EVENTARGUMENT'] = combo.arbitr.get_EVENTARGUMENT
                post_arbitr['__VIEWSTATE'] = combo.arbitr.get_VIEWSTATE
                post_arbitr['__VIEWSTATEGENERATOR'] = combo.arbitr.get_VIEWSTATEGENERATOR
                post_arbitr['__PREVIOUSPAGE'] = combo.arbitr.get_PREVIOUSPAGE
                post_arbitr['__EVENTVALIDATION'] = combo.arbitr.get_EVENTVALIDATION
                post_arbitr['ctl00$cphBody$ArbitrManagerList1$tbLastName'] = name[0]
                post_arbitr['ctl00$cphBody$ArbitrManagerList1$tbFirstName'] = name[1]
                post_arbitr['ctl00$cphBody$ArbitrManagerList1$tbMiddleName'] = name[2]
                yield SplashFormRequest(response.url, callback=self.parse_serp_arbitr, formdata=post_arbitr,
                                        endpoint='execute',
                                        method='POST',
                                        cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                        slot_policy=SlotPolicy.PER_DOMAIN,
                                        session_id=1,
                                        errback=self.errback_httpbin, dont_filter=True,
                                        cb_kwargs={'attemp': attemp, 'name': name, 'original_name': a})

    async def parse_serp_arbitr(self, response, attemp, name, original_name):
        """page with arbitr search result  /"""
        combo = Combo(response_=response)
        soup = BS(str(response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        links = soup.find_all(href=re.compile('ArbitrManagerCard\.aspx'))
        count_links = len(links)
        if len(name) == 3 and name[2] == ' ':
            new_name = list()
            new_name.append(name[0])
            new_name.append(name[2])
            new_name.append(name[1])
            name = new_name
        if attemp == 0 and len(links) == 0:
            attemp += 1
            post_arbitr['ctl00$cphBody$ArbitrManagerList1$tbLastName'] = name[2].strip()
            post_arbitr['ctl00$cphBody$ArbitrManagerList1$tbFirstName'] = name[0].strip()
            post_arbitr['ctl00$cphBody$ArbitrManagerList1$tbMiddleName'] = name[1].strip()
            yield SplashFormRequest(response.url, self.parse_serp_arbitr, formdata=post_arbitr,
                                    endpoint='execute',
                                    method='POST',
                                    cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    session_id=1,
                                    errback=self.errback_httpbin, dont_filter=True,
                                    cb_kwargs={'attemp': attemp, 'name': name, 'original_name': original_name})

        for link in links:
            yield SplashRequest(self.url_spider.url_join(start_link, link.get('href')), callback=self.card_arbitr,
                                endpoint='execute',
                                method='GET',
                                cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                session_id=1,
                                errback=self.errback_httpbin,
                                cb_kwargs={'count_links': count_links, 'original_name': original_name})

    async def card_arbitr(self, response, count_links, original_name):
        """parsing arbitr card"""
        combo = Combo(response_=response)
        locator = ArbitrLocators()
        loader = ArbitrItem(CrawlerFedresursItem(), response=response)
        loader.add_value('links_count', count_links)
        loader.add_value('item_transfer', original_name)
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
                if get_id == locator.inn_loc:
                    loader.add_value('inn', row.findAll('td')[1].get_text().strip())
                if get_id == locator.registration_number_loc:
                    loader.add_value('registration_number', row.findAll('td')[1].get_text().strip())
                if get_id == locator.registration_date_loc:
                    loader.add_value('registration_date', row.findAll('td')[1].get_text().strip())
                if get_id == locator.sro_loc:
                    loader.add_value('sro', row.findAll('td')[1].get_text().strip())
                if get_id == locator.entry_date_loc:
                    loader.add_value('entry_date', row.findAll('td')[1].get_text().strip())
                loader.add_value('created_at', return_parse_date())
            loader.add_value('item_type', ARBITR_NAME)
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
