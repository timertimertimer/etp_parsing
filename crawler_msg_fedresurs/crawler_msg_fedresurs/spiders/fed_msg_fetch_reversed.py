# -*- coding: utf-8 -*-

import logging
from random import randint

import pandas as pd
from scrapy import FormRequest
from scrapy.spidermiddlewares.httperror import HttpError
from scrapy.spiders import Spider
from scrapy_splash import SplashRequest, SlotPolicy
from twisted.internet.error import DNSLookupError, TCPTimedOutError

from ..items import CrawlerMsgFedresursItem, MsgFedresursItemLoader
from ..manage_spider.app import ComboMsg
from ..settings import DEFAULT_REQUESTS_HEADERS
from ..utils.config import *
from ..utils.data_for_request import script_lua, script_lua_category, post_headers, request_headers_msg, \
    headers_msg_page
from ..utils.post_data_msg import post_data, post_data_pagination
from ..utils.work_with_text_and_number_cookies import cookie_parser
from ..utils.working_with_time import increase_time_days, return_parse_date
from ..utils.working_with_url import UrlConfig

logger = logging.getLogger(__name__)


class FedMsgFetchSpider(Spider):
    name = 'fed_msg_fetch_reversed'

    def __init__(self, *args, **kwargs):
        super(FedMsgFetchSpider, self).__init__(*args, **kwargs)
        self.url_spider = UrlConfig()
        self.link_set = set()

    def start_requests(self):
        """start requests """
        yield SplashRequest(self.url_spider.parse_url(start_link), self.go_to_msg_page, endpoint='execute',
                            cache_args=['lua_source'], args={'lua_source': script_lua},
                            slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=DEFAULT_REQUESTS_HEADERS,
                            session_id=1,
                            errback=self.errback_httpbin)

    def go_to_msg_page(self, response):
        """make request from main page to msg page for save cookies"""
        date_range = pd.date_range(start_time_from, periods=periods_, freq=format_period)
        for start_time in reversed(date_range):
            yield SplashRequest(self.url_spider.parse_url(message_page), callback=self.iterate_throught_types,
                                endpoint='execute', cache_args=['lua_source'], args={'lua_source': script_lua},
                                slot_policy=SlotPolicy.PER_DOMAIN, splash_headers=DEFAULT_REQUESTS_HEADERS,
                                session_id=1, dont_filter=True, cb_kwargs={'start_time': start_time},
                                errback=self.errback_httpbin)

    def iterate_throught_types(self, response, start_time):
        combo = ComboMsg(response_=response)
        # types_set -> set with message types
        types_set = combo.minfo.return_msg_types_set()
        for v in types_set:
            start_time_str = start_time.strftime('%d.%m.%Y')
            end_time = f'{increase_time_days(start_time_str, time_delta)}'
            search_x = randint(33, 60)
            search_y = randint(8, 11)
            post_data['ctl00$cphBody$ibMessagesSearch.x'] = str(search_x)
            post_data['ctl00$cphBody$ibMessagesSearch.y'] = str(search_y)
            viewstate = combo.minfo.get_VIEWSTATE
            viewstategenerator = combo.minfo.get_VIEWSTATEGENERATOR
            previouspage = combo.minfo.get_PREVIOUSPAGE
            post_data['__EVENTTARGET'] = combo.minfo.get_EVENTTARGET
            post_data['__EVENTARGUMENT'] = combo.minfo.get_EVENTARGUMENT
            post_data['__VIEWSTATE'] = viewstate
            post_data['__VIEWSTATEGENERATOR'] = viewstategenerator
            post_data['__PREVIOUSPAGE'] = previouspage
            post_data['ctl00$cphBody$mdsMessageType$tbSelectedText'] = re.sub(r'\s+', ' ', v[0])
            post_data['ctl00$cphBody$mdsMessageType$hfSelectedValue'] = re.sub(r'\s+', ' ', v[1])
            post_data['ctl00$cphBody$cldrBeginDate$tbSelectedDate'] = start_time_str
            post_data['ctl00$cphBody$cldrBeginDate$tbSelectedDateValue'] = start_time_str
            post_data['ctl00$cphBody$cldrEndDate$tbSelectedDate'] = end_time
            post_data['ctl00$cphBody$cldrEndDate$tbSelectedDateValue'] = end_time
            url_quote_text = self.url_spider.make_url_quote(
                post_data['ctl00$cphBody$mdsMessageType$tbSelectedText'])
            cookies = response.data['cookies']
            cookies_ = combo.minfo.complex_cookie(cookies=cookies, text=url_quote_text,
                                                  type_=post_data[
                                                      'ctl00$cphBody$mdsMessageType$hfSelectedValue'],
                                                  date_from=post_data[
                                                      'ctl00$cphBody$cldrBeginDate$tbSelectedDateValue'],
                                                  date_to=post_data[
                                                      'ctl00$cphBody$cldrEndDate$tbSelectedDateValue'])
            post_headers['cookie'] = cookies_
            post_headers['referer'] = response.url
            yield FormRequest.from_response(response, callback=self.get_list_of_links, formdata=post_data,
                                            headers=post_headers,
                                            dont_filter=True, encoding='utf-8',
                                            cb_kwargs={
                                                'viewstate': viewstate,
                                                'viewstategenerator': viewstategenerator,
                                                'previouspage': previouspage,
                                                'msg_type': v[0],
                                                'msg_type_eng': v[1],
                                                'current_page_arg': 1,
                                                'time_start': start_time_str,
                                                'end_time': end_time,
                                                'only_cookies': cookies_},
                                            errback=self.errback_httpbin)

    async def get_list_of_links(self, response, msg_type, msg_type_eng, time_start, end_time, current_page_arg,
                                viewstate, viewstategenerator, previouspage, only_cookies):
        """ parse page get links to msg page """
        combo = ComboMsg(response_=response)
        # set_links_to_msg_page = set()
        lst_links = combo.minfo.link_to_msg_page()
        for link in lst_links:
            attemp = 0
            link = combo.minfo.get_only_href(link)
            link = self.url_spider.url_join(start_link, link)
            headers_msg_page[':path'] = '/' + link.split('/')[-1]
            headers_msg_page['referer'] = response.url
            yield FormRequest(self.url_spider.parse_url(link), callback=self.parse_msg_page, method='POST',
                              cookies=cookie_parser(only_cookies),
                              headers=headers_msg_page,
                              errback=self.errback_httpbin,
                              cb_kwargs={'attemp': attemp, 'link': link, 'msg_type': msg_type})

        # check if pagination correct. AND if correct, send request to next page
        if next_page := combo.minfo.get_next_page:
            try:
                if (current_page_arg == next_page - 1) and (re.match(r'^\d+$', str(next_page))) and (
                        isinstance(next_page, int)):
                    kwargs_data = {'msg_type': msg_type, 'msg_type_eng': msg_type_eng, 'time_start': time_start,
                                   'end_time': end_time, 'current_page': current_page_arg, 'next_page': next_page,
                                   'viewstate': viewstate, 'viewstategenerator': viewstategenerator,
                                   'previouspage': previouspage
                                   }
                    post_data_pagination['__EVENTTARGET'] = combo.minfo.get_EVENTTARGET_from_tag(
                        combo.minfo.return_tag_a_pagination)
                    post_data_pagination['ctl00$PrivateOffice1$ctl00'] = post_privat_office + '|' + \
                                                                         post_data_pagination['__EVENTTARGET']
                    post_data_pagination['__EVENTARGUMENT'] = f'Page${kwargs_data["next_page"]}'
                    post_data_pagination['__VIEWSTATE'] = kwargs_data['viewstate']
                    post_data_pagination['__VIEWSTATEGENERATOR'] = kwargs_data['viewstategenerator']
                    post_data_pagination['__PREVIOUSPAGE'] = kwargs_data['previouspage']
                    post_data_pagination['ctl00$cphBody$mdsMessageType$tbSelectedText'] = kwargs_data['msg_type']
                    post_data_pagination['ctl00$cphBody$mdsMessageType$hfSelectedValue'] = kwargs_data['msg_type_eng']
                    post_data_pagination['ctl00$cphBody$cldrBeginDate$tbSelectedDate'] = kwargs_data['time_start']
                    post_data_pagination['ctl00$cphBody$cldrBeginDate$tbSelectedDateValue'] = kwargs_data['time_start']
                    post_data_pagination['ctl00$cphBody$cldrEndDate$tbSelectedDate'] = kwargs_data['end_time']
                    post_data_pagination['ctl00$cphBody$cldrEndDate$tbSelectedDateValue'] = kwargs_data['end_time']
                    url_quote_text = self.url_spider.make_url_quote(
                        post_data_pagination['ctl00$cphBody$mdsMessageType$tbSelectedText'])
                    cookies = only_cookies
                    request_headers_msg['referer'] = response.url
                    request_headers_msg['user-agent'] = DEFAULT_REQUESTS_HEADERS['User-Agent']
                    cookies_ = combo.minfo.complex_cookie(cookies=cookies, text=url_quote_text,
                                                          type_=post_data_pagination[
                                                              'ctl00$cphBody$mdsMessageType$hfSelectedValue'],
                                                          date_from=post_data_pagination[
                                                              'ctl00$cphBody$cldrBeginDate$tbSelectedDateValue'],
                                                          date_to=post_data_pagination[
                                                              'ctl00$cphBody$cldrEndDate$tbSelectedDateValue'])
                    page_for_cookie = 0
                    if kwargs_data["next_page"] >= 3:
                        page_for_cookie += kwargs_data["current_page"] - 2
                    new_cookie = (''.join(
                        re.sub(r'PageNumber=\d{1,2}', f'PageNumber={str(page_for_cookie)}', cookies_, flags=re.I)))
                    current_page_arg = kwargs_data['current_page'] + 1
                    yield FormRequest(response.url, callback=self.get_list_of_links,
                                      formdata=post_data_pagination,
                                      cookies=cookie_parser(new_cookie),
                                      headers=request_headers_msg, dont_filter=True,
                                      encoding='utf-8',
                                      cb_kwargs={'viewstate': kwargs_data['viewstate'],
                                                 'viewstategenerator': kwargs_data['viewstategenerator'],
                                                 'previouspage': kwargs_data['previouspage'],
                                                 'msg_type': kwargs_data['msg_type'],
                                                 'msg_type_eng': kwargs_data['msg_type_eng'],
                                                 'current_page_arg': current_page_arg,
                                                 'time_start': kwargs_data['time_start'],
                                                 'end_time': kwargs_data['end_time'],
                                                 'only_cookies': only_cookies},
                                      errback=self.errback_httpbin
                                      )
                else:
                    logger.error(f'{msg_type}::{time_start}::ERROR PAGINATION SEQUENCE. This is {next_page}"')
            except Exception as e:
                logger.error(f'{msg_type}::{time_start}::VALUE ERROR "next page not integer"\n{e}\nThis is {next_page}',
                             exc_info=True)

    async def parse_msg_page(self, response, attemp, link, msg_type):
        loader = MsgFedresursItemLoader(CrawlerMsgFedresursItem(), response=response)
        combo = ComboMsg(response_=response)
        # msg_type_ like on fedresurs
        msg_type_ = combo.mpage.get_msg_type(msg_type)
        if msg_type_ and escape_words.strip() not in msg_type_:
            msg_type_iteration = msg_type
            loader.add_value('message_link', link)
            loader.add_value('message_type', msg_type_)
            loader.add_value('message_number', combo.mpage.get_msg_number)
            loader.add_value('publish_date', combo.mpage.get_publicat_date())
            loader.add_value('case_number', combo.mpage.get_case_number())
            loader.add_value('debtor_inn', combo.mpage.get_debtor_inn())
            if msg_type_iteration in announce_msg_trade:
                loader.add_value('lots', combo.announce.get_all_lots())
                # debtor name & debtor address only for "Объявление о проведении торгов"
                loader.add_value('debtor_name', combo.mpage.get_deb_name())
                loader.add_value('debtor_address', combo.mpage.get_debtor_address())

            if msg_type_iteration in canceled_msg_ad:
                loader.add_value('canceled_message', combo.cancele_msg.canceled_message())
            # announced_message only for "Сообщение о результатах торгов"
            if msg_type_iteration in public_tender_msg:
                loader.add_value('announced_message', combo.msgresult.tendering_message())
                loader.add_value('lots', combo.msgresult.get_all_lots_tender())
                loader.add_value('files', combo.mpage.managed_files(msg_type_))
            if msg_type_iteration in modified_message_msg:
                loader.add_value('modified_message', combo.changed_msg.changed_message())
            # WORKING WITH FILES
            if msg_type_iteration in [announce_msg_trade, public_tender_msg, report_of_valuer]:
                loader.add_value('files', combo.mpage.managed_files(msg_type_iteration))
            loader.add_value('created_at', return_parse_date())

            yield loader.load_item()
        else:
            if attemp == 0:
                attemp += 1
                yield SplashRequest(link, callback=self.parse_msg_page,
                                    splash_headers=headers_msg_page,
                                    endpoint='execute',
                                    cache_args=['lua_source'], args={'lua_source': script_lua_category},
                                    slot_policy=SlotPolicy.PER_DOMAIN,
                                    dont_filter=True,
                                    errback=self.errback_httpbin,
                                    cb_kwargs={'attemp': attemp, 'link': link, 'msg_type': msg_type},
                                    encoding='utf-8', session_id=2)
            if attemp == 1:
                logger.error(f'{response.url} :: TYPE MSG ERROR')


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
