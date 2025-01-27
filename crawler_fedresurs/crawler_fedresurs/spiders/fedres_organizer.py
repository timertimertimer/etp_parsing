# -*- coding: utf-8 -*-
from bs4 import BeautifulSoup as BS
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import CrawlSpider
from scrapy_splash import SlotPolicy, SplashRequest, SplashFormRequest
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from crawler_fedresurs.settings import DEFAULT_REQUESTS_HEADERS
from crawler_fedresurs.utils.data_for_requests import script_lua, script_lua_category
from ..items import CrawlerFedresursItem, OrgCompanyItem, OrgNameItem
from ..locators.organizer_locator import OrgCompanyLocator, OrgNameLocator
from ..manage_spiders.app import Combo
from ..utils.config import *
from ..utils.connect_for_change_status import SetValueDb
from ..utils.post_data_org_company import post_org_company
from ..utils.post_data_org_name import post_follow_org_name_form, post_org_name
from ..utils.read_org_name_and_company import ReadOrgName
from ..utils.work_with_text_and_number import return_company_cut, return_clean_name
from ..utils.working_with_time import return_parse_date
from ..utils.working_with_url import UrlConfig
import time


class FedresOrganizerSpider(CrawlSpider):
    name = 'fedres_organizer'
    # allowed_domains = ['bankrot.fedresurs.ru']
    # start_urls = ['https://bankrot.fedresurs.ru']

    custom_settings = {
        'SPLASH_URL': SPLASH_URL_ORGANIZER,
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
            'crawler_fedresurs.pipelines.DbConnectOrganizer': 350,
            'crawler_fedresurs.pipelines.ManageTaskTable': 370,
        }
    }

    def __init__(self, *args, **kwargs):
        super(FedresOrganizerSpider, self).__init__(*args, **kwargs)
        self.url_spider = UrlConfig()
        self.organizer = ReadOrgName()
        self.ch_value = SetValueDb()

    def start_requests(self):
        """befor yield first request -> get data for query from files and then delete files"""
        org_company = self.organizer.get_org_company_data()
        org_name = self.organizer.get_org_name_data()
        # ---- after get all data from file delete them and back to project dir
        os.chdir(DIR_ORGANIZER)
        time.sleep(0.5)
        os.system('rm post_data_organizer*.json')
        time.sleep(0.5)
        os.chdir(DIR_PROJECT)

        yield SplashRequest(self.url_spider.parse_url(start_link), self.parse_main_page, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=DEFAULT_REQUESTS_HEADERS,
                            session_id=1,
                            errback=self.errback_httpbin, cb_kwargs={'name': org_name, 'company': org_company})

    def parse_main_page(self, response, name, company):
        """after receiving cookies go to Organizer page"""
        yield SplashRequest(org_link, callback=self.sort_category,
                            endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua_category},
                            slot_policy=SlotPolicy.PER_DOMAIN,
                            session_id=1,
                            errback=self.errback_httpbin, cb_kwargs={'name': name, 'company': company})

    async def sort_category(self, response, name, company):
        """run function according query data"""
        organizer_name = name
        organizer_company = company
        combo = Combo(response_=response)
        if len(organizer_name) > 0:
            post_follow_org_name_form['__EVENTTARGET'] = combo.arbitr.get_EVENTTARGET
            post_follow_org_name_form['__EVENTARGUMENT'] = combo.arbitr.get_EVENTARGUMENT
            post_follow_org_name_form['__VIEWSTATE'] = combo.arbitr.get_VIEWSTATE
            post_follow_org_name_form['__VIEWSTATEGENERATOR'] = combo.arbitr.get_VIEWSTATEGENERATOR
            post_follow_org_name_form['__PREVIOUSPAGE'] = combo.arbitr.get_PREVIOUSPAGE
            yield SplashFormRequest(org_link, callback=self.select_org_name_page,
                                    formdata=post_follow_org_name_form,
                                    endpoint='execute',
                                    cache_args=['lua_source'],
                                    method='POST',
                                    args={'lua_source': script_lua_category},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    session_id=1,
                                    errback=self.errback_httpbin, dont_filter=True,
                                    cb_kwargs={'organizer_name': organizer_name})

        if len(organizer_company) > 0:
            for d in organizer_company:
                self.ch_value.change_status_organizer(ORGANIZER_ALL, d, 'failed')
                attemp = 0
                original_name = d
                post_org_company['__EVENTTARGET'] = combo.arbitr.get_EVENTTARGET
                post_org_company['__EVENTARGUMENT'] = combo.arbitr.get_EVENTARGUMENT
                post_org_company['__VIEWSTATE'] = combo.arbitr.get_VIEWSTATE
                post_org_company['__VIEWSTATEGENERATOR'] = combo.arbitr.get_VIEWSTATEGENERATOR
                post_org_company['__PREVIOUSPAGE'] = combo.arbitr.get_PREVIOUSPAGE
                post_org_company['ctl00$cphBody$tbOrgName'] = d.replace('\'', '"')
                yield SplashFormRequest(response.url, callback=self.parse_serp_page_company, formdata=post_org_company,
                                        endpoint='execute',
                                        method='POST',
                                        cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                        slot_policy=SlotPolicy.PER_DOMAIN,
                                        session_id=1,
                                        errback=self.errback_httpbin, dont_filter=True,
                                        cb_kwargs={'company': d, 'postdata': post_org_company, 'attemp': attemp,
                                                   'original_name': original_name})

    async def select_org_name_page(self, response, organizer_name):
        """after make formdata=post_follow_org_name_form we are on org_name page"""
        for d in organizer_name:
            self.ch_value.change_status_organizer(ORGANIZER_ALL, d, 'failed')
            fullname_ = ''.join(return_clean_name(d)).split(' ')
            attemp = 0
            if len(fullname_) == 2:
                fullname_.append(' ')
            if len(fullname_) >= 3:
                post_org_name['__EVENTTARGET'] = post_follow_org_name_form['__EVENTTARGET']
                post_org_name['__EVENTARGUMENT'] = post_follow_org_name_form['__EVENTARGUMENT']
                post_org_name['__VIEWSTATE'] = post_follow_org_name_form['__VIEWSTATE']
                post_org_name['__VIEWSTATEGENERATOR'] = post_follow_org_name_form['__VIEWSTATEGENERATOR']
                post_org_name['__PREVIOUSPAGE'] = post_follow_org_name_form['__PREVIOUSPAGE']
                post_org_name['ctl00$cphBody$tbPrsLastName'] = fullname_[0]
                post_org_name['ctl00$cphBody$tbPrsFirstName'] = fullname_[1]
                post_org_name['ctl00$cphBody$tbPrsMiddleName'] = fullname_[2]
                yield SplashFormRequest(response.url, self.parse_serp_page_org_name,
                                        formdata=post_org_name,
                                        endpoint='execute',
                                        method='POST',
                                        cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                        slot_policy=SlotPolicy.PER_DOMAIN,
                                        session_id=1,
                                        errback=self.errback_httpbin, dont_filter=True,
                                        cb_kwargs={'attemp': attemp, 'name': fullname_, 'original_name': d})

    async def parse_serp_page_org_name(self, response, attemp, name, original_name):
        """/PrsTOCard.aspx?"""
        soup = BS(str(response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        links = soup.find_all(href=re.compile('/PrsTOCard.aspx'))
        count_links = len(links)
        if len(name) == 3 and name[2] == ' ':
            # if third -> empty string, second -> lastname, first -> name do reverse
            new_name = list()
            new_name.append(name[0])
            new_name.append(name[2])
            new_name.append(name[1])
            name = new_name
        if attemp == 0 and len(links) == 0:
            attemp += 1
            post_org_name['ctl00$cphBody$tbPrsLastName'] = name[2].strip()
            post_org_name['ctl00$cphBody$tbPrsFirstName'] = name[0].strip()
            post_org_name['ctl00$cphBody$tbPrsMiddleName'] = name[1].strip()
            yield SplashFormRequest(response.url, self.parse_serp_page_org_name,
                                    formdata=post_org_name,
                                    endpoint='execute',
                                    method='POST',
                                    cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    session_id=1,
                                    errback=self.errback_httpbin, dont_filter=True,
                                    cb_kwargs={'attemp': attemp, 'name': name,
                                               'original_name': original_name})
        if links and len(links) >= 1:
            for link in links:
                yield SplashRequest(self.url_spider.url_join(start_link, link.get('href')),
                                    callback=self.parse_page_name,
                                    endpoint='execute',
                                    cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    session_id=1,
                                    errback=self.errback_httpbin,
                                    cb_kwargs={'original_name': original_name, 'count_links': count_links})

    async def parse_page_name(self, response, original_name, count_links):
        """parsing card of organizer person"""
        locator = OrgNameLocator()
        loader = OrgNameItem(CrawlerFedresursItem(), response=response)
        combo = Combo(response_=response)
        loader.add_value('links_count', count_links)
        loader.add_value('item_type2', ORGANIZER_ALL)
        loader.add_value('item_type', ORG_NAME)
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
                if get_id == locator.address_loc:
                    loader.add_value('address', row.findAll('td')[1].get_text().strip())
                if get_id == locator.phone_loc:
                    loader.add_value('phone', row.findAll('td')[1].get_text().strip())
                if get_id == locator.region_loc:
                    loader.add_value('region', row.findAll('td')[1].get_text().strip())
                if get_id == locator.inn_loc:
                    loader.add_value('inn', row.findAll('td')[1].get_text().strip())
                if get_id == locator.ogrn_loc:
                    loader.add_value('ogrn', row.findAll('td')[1].get_text().strip())

            loader.add_value('created_at', return_parse_date())
            loader.add_value('link', response.url)
            loader.add_value('full_name', combo.arbitr.full_name_return(lastname, firstname, midname))
        yield loader.load_item()

    async def parse_serp_page_company(self, response, company, postdata, attemp, original_name):
        """parsing page with post result of companyies"""
        combo = Combo(response_=response)
        soup = BS(str(response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        links = soup.find_all(href=re.compile(r'OrgTOCard\.aspx'))
        count_links = len(links)
        if len(links) == 0 and attemp == 0:
            if '«' in company:
                company = ''.join(company).replace('«', '"').replace('»', '"')
            elif '"' in company:
                company = combo.orgcomp.double_quote_into_arrow(company)
            else:
                company = return_company_cut(company_=company)
            postdata['ctl00$cphBody$tbOrgName'] = company
            attemp += 1
            yield SplashFormRequest(response.url, self.parse_serp_page_company, formdata=postdata,
                                    endpoint='execute',
                                    method='POST',
                                    cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    session_id=1,
                                    errback=self.errback_httpbin, dont_filter=True,
                                    cb_kwargs={'company': company, 'postdata': postdata, 'attemp': attemp,
                                               'original_name': original_name})
        if len(links) == 0 and attemp == 1:
            if '«' in company or '"' in company:
                company = return_company_cut(company_=company)
                attemp += 1
                postdata['ctl00$cphBody$tbOrgName'] = company
                yield SplashFormRequest(response.url, self.parse_serp_page_company, formdata=postdata,
                                        endpoint='execute',
                                        method='POST',
                                        cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                        slot_policy=SlotPolicy.PER_DOMAIN,
                                        session_id=1,
                                        errback=self.errback_httpbin, dont_filter=True,
                                        cb_kwargs={'company': company, 'postdata': postdata, 'attemp': attemp,
                                                   'original_name': original_name})
        if len(links) >= 1:
            for link in links:
                yield SplashRequest(self.url_spider.url_join(start_link, link.get('href')),
                                    callback=self.parse_page_company,
                                    endpoint='execute',
                                    cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    session_id=1, dont_filter=False,
                                    errback=self.errback_httpbin,
                                    cb_kwargs={'original_name': original_name, 'count_links': count_links})

    async def parse_page_company(self, response, original_name, count_links):
        """parsing card of company"""
        locator = OrgCompanyLocator()
        loader = OrgCompanyItem(CrawlerFedresursItem(), response=response)
        loader.add_value('links_count', count_links)
        loader.add_value('item_type2', ORGANIZER_ALL)
        loader.add_value('item_type', ORG_COMPANY)
        loader.add_value('item_transfer', original_name)
        soup = BS(str(response.text).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        table = soup.find('table', id='ctl00_cphBody_tblSroCardInfo')
        if table is None:
            table = soup.find('table', class_='au')
        if table:
            for row in table.find_all('tr'):
                get_id = row.get('id')
                if get_id == locator.short_name_loc:
                    loader.add_value('short_name', row.findAll('td')[1].get_text().strip())
                if get_id == locator.full_name_loc:
                    loader.add_value('full_name', row.findAll('td')[1].get_text().strip())
                if get_id == locator.address_loc:
                    loader.add_value('address', row.findAll('td')[1].get_text().strip())
                if get_id == locator.address_loc:
                    loader.add_value('address', row.findAll('td')[1].get_text().strip())
                if get_id == locator.phone_loc:
                    loader.add_value('phone', row.findAll('td')[1].get_text().strip())
                if get_id == locator.region_loc:
                    loader.add_value('region', row.findAll('td')[1].get_text().strip())
                if get_id == locator.inn_loc:
                    loader.add_value('inn', row.findAll('td')[1].get_text().strip())
                if get_id == locator.ogrn_loc:
                    loader.add_value('ogrn', row.findAll('td')[1].get_text().strip())
                if get_id == locator.kpp_loc:
                    loader.add_value('kpp', row.findAll('td')[1].get_text().strip())
                if get_id == locator.legal_form_loc:
                    loader.add_value('legal_form', row.findAll('td')[1].get_text().strip())
            loader.add_value('created_at', return_parse_date())
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
