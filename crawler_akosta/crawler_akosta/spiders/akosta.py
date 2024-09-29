from icecream import ic
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import Spider
from scrapy import Request, FormRequest
from scrapy_splash import SplashRequest, SlotPolicy, SplashFormRequest
from twisted.internet.error import DNSLookupError, TCPTimedOutError, TimeoutError

from ..manage_spider.app import Combo
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..utils.data_for_requests import script_lua, script_lua_nojs
from ..utils.headers import HEADERS_TO_SERP_PAGE
from ..utils.post_data import post_data_pagination, post_data_to_trade, post_data_query
from ..utils.config import start_page, end_page, data_origin_url, search_link, start_time, end_time
from ..utils.work_with_text_and_number import return_main_cookies, cookie_parser
from ..utils.working_with_time import return_servertime
from ..items import CrawlerAkostaItem, CrawlerAkostaItemLoader
from ..utils.download import DownloadFiles, USER_AGENT
import copy
import logging
import json
import csv

logger = logging.getLogger(__name__)


class AkostaSpider(Spider):
    name = 'akosta'
    # allowed_domains = ['www.akosta.info/akosta/lots.xhtml']
    start_url = ['https://www.akosta.info/']

    # start_url = ['https://httpbin.org/']

    def __init__(self, *args, **kwargs):
        super(AkostaSpider, self).__init__(*args, **kwargs)
        self.down = DownloadFiles()

    def start_requests(self):
        yield SplashRequest(self.start_url[0], self.parse_main_page, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=DEFAULT_REQUESTS_HEADERS,
                            errback=self.errback_httpbin)

    def parse_main_page(self, response):
        """parse main page and get link to serp page"""
        combo = Combo(_response=response)
        link = combo.pre.get_link_to_serp_trade
        yield SplashRequest(link, self.before_request_query,
                            endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=HEADERS_TO_SERP_PAGE,
                            errback=self.errback_httpbin)

    def before_request_query(self, response):
        """ make post request for searching into current period of time """
        combo = Combo(_response=response)
        headers_ = copy.deepcopy(HEADERS_TO_SERP_PAGE)
        headers_['Referer'] = response.url
        viewstate = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        post_data_query["formMain:inputServerTime"] = return_servertime()
        post_data_query["javax.faces.ViewState"] = viewstate
        post_data_query["formMain:fromIdAcceptancePeriod_input"] = start_time
        post_data_query["formMain:toIdAcceptancePeriod_input"] = end_time
        cookie = response.data['cookies']
        cookie = return_main_cookies(cookie)
        yield SplashFormRequest(response.url, self.after_post_request, formdata=post_data_query,
                                endpoint='execute',
                                cache_args=['lua_source'], args={'lua_source': script_lua_nojs},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                cb_kwargs={'_header': headers_, 'cookie': cookie, 'viewstate': viewstate})

    def after_post_request(self, response, _header, cookie, viewstate):
        """ after redirect -> make GET request """
        cookie_ = cookie
        if cookie_:
            url = 'https://www.akosta.info/akosta/lots.xhtml'
            yield SplashRequest(url, self.parse_pagination,
                                endpoint='execute',
                                cache_args=['lua_source'], args={'lua_source': script_lua},
                                slot_policy=SlotPolicy.PER_DOMAIN,
                                errback=self.errback_httpbin,
                                cb_kwargs={'_header': _header, 'cookie_': cookie, 'page_number': 1,
                                           'viewstate': viewstate, 'total_pages': 0})
        else:
            logger.error(f'{response.url} :: error cookie in "after_post_request" function ')

    def parse_pagination(self, response, _header, cookie_, page_number, viewstate, total_pages, ):
        """parse page with form  for searching lots in current period
         and put all post_data_query(like links) to list
        """
        list_with_links = list()
        combo = Combo(_response=response)
        viewstate_ = viewstate
        if page_number == 1:
            current_page, total_pages = combo.pre.get_total_and_current_page
            for tag_tr in combo.pre.get_trade_links():
                _id_post_data = combo.pre.get_id_a_trade_1(tag_tr)
                trading_id_text = combo.pre.get_trading_number_1(_id_post_data, page_number)
                list_with_links.append(('trading_number', trading_id_text))
        else:
            # cuurent page is not important
            current_page = page_number
            total_pages = total_pages
            list_with_links = combo.pre.get_trade_links_2(page_number, total_pages)

        for data in list_with_links:
            try:
                with open('data_parse.csv', 'a') as csv_file:
                    csv_writer = csv.writer(csv_file)
                    csv_writer.writerow([x for x in data])

            except IndexError as er:
                logger.error(f'ERROR write to csv file - {data} :: {er}')
                continue

            post_data_to_trade['javax.faces.source'] = data[1]
            form_main = post_data_to_trade['javax.faces.source']
            post_data_to_trade[form_main] = form_main
            post_data_to_trade["formMain:inputServerTime"] = return_servertime()
            post_data_to_trade["formMain:fromIdAcceptancePeriod_input"] = start_time
            post_data_to_trade["javax.faces.ViewState"] = data[0]
            post_data_ = copy.deepcopy(post_data_to_trade)
            del post_data_to_trade[form_main]
            headers_1 = copy.deepcopy(_header)
            headers_1['Referer'] = response.url
            headers_1['Connection'] = 'close'
            headers_1['Faces-Request'] = 'partial/ajax'
            headers_1['Sec-Fetch-Dest'] = 'empty'
            headers_1['Sec-Fetch-Mode'] = 'cors'
            headers_1['Sec-Fetch-Site'] = 'same-origin'
            headers_1['User-Agent'] = USER_AGENT

            headers_1['Cookie'] = str(cookie_).strip()
            headers_1['Origin'] = 'https://www.akosta.info'
            headers_1['sec-gpc'] = '1'

        if current_page < total_pages:
            page_number += 1
            data_lots = int(page_number) * 50 - 50
            post_data_pagination["formMain:lotListTable_first"] = str(data_lots)
            post_data_pagination["formMain:inputServerTime"] = return_servertime()
            post_data_pagination["javax.faces.ViewState"] = viewstate
            _header['Connection'] = 'close'
            yield SplashFormRequest(response.url, callback=self.parse_pagination, formdata=post_data_pagination,
                                    endpoint='execute', splash_headers=_header, dont_filter=True,
                                    cache_args=['lua_source'], args={'lua_source': script_lua},
                                    slot_policy=SlotPolicy.PER_DOMAIN, errback=self.errback_httpbin,
                                    cb_kwargs={'page_number': page_number, 'cookie_': cookie_,
                                               '_header': _header,
                                               'viewstate': viewstate_,
                                               'total_pages': total_pages})

    def errback_httpbin(self, failure):
        # logs failures

        self.logger.error(repr(failure))

        if failure.check(HttpError):
            response = failure.value.response
            self.logger.error("HttpError occurred on %s", response.url, )

        elif failure.check(DNSLookupError):
            request = failure.request
            self.logger.error("DNSLookupError occurred on %s", request.url)

        elif failure.check(TimeoutError, TCPTimedOutError):
            request = failure.request
            self.logger.error("TimeoutError occurred on %s", request.url)

    @staticmethod
    def error_to_redirect(post_data):
        logger.error(f'{post_data}')

    @staticmethod
    def error_pagintaion(page_number):
        logger.error(f'{page_number} :: ERROR PAGINATION')
