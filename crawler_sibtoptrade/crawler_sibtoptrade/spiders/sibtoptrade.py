# -*- coding: utf-8 -*-
from icecream import ic

from ..config import *
from scrapy.spiders import CrawlSpider
from scrapy_splash import SplashRequest
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
import scrapy_splash
from ..items import SibtopItem, SibtopItemLoader, DownlodItem, check_trading_type
from ..manage import *
from ..download import DownloadFiles
from scrapy import Request
import pathlib
from bs4 import BeautifulSoup as BS
from itertools import chain

import logging
from ..locator import *

logger = logging.getLogger(__name__)


class SibtoptradeSpider(CrawlSpider):
    name = bot_name
    allowed_domains = ['sibtoptrade.ru']
    total_iterations = int(finish_page) - int(start_page)

    start_url_ = [start_urls.format(n + int(start_page))
                  for n in range(total_iterations)]

    def start_requests(self):
        yield SplashRequest(start_urls1, self.iterrate_througth_pages,
                            endpoint='execute',
                            cache_args=['lua_source'],
                            args={'lua_source': script_lua},
                            slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
                            headers=headers_brow, session_id=1, errback=self.errback_httpbin)

    def iterrate_througth_pages(self, response):
        last_page = response.xpath('//nav[@class="pagination"]//li[last()]/a/text()').get()
        for url in self.start_url_:
            current_page = ''.join(re.findall(r'https://sibtoptrade.ru/trade/bankruptcy/#state=1&page=(\d+).*', url))
            if int(last_page) >= int(current_page):
                yield SplashRequest(url, self.parse,
                                    endpoint='execute',
                                    cache_args=['lua_source'],
                                    args={'lua_source': script_lua},
                                    slot_policy=scrapy_splash.SlotPolicy.PER_DOMAIN,
                                    headers=headers_brow, session_id=1, errback=self.errback_httpbin, dont_filter=True)

    def parse(self, response):
        logger.info(f'NOW WE ON PAGE {response.url}')
        # ###_set_cookies_request_to_trading_page_###
        # try:
        #     ###_if_cookies_in_list_format.__GET_DICT_FROM_LIST_###
        #     cookies = response.data['cookies']
        #     for c in cookies:
        #         cookies = c
        # except:
        #     cookie = (response.headers['Set-Cookie']).decode('utf-8')
        #     cookies = cookie_parser(cookie)
        # ic(cookies)
        soup = BS(str(response.body.decode('utf-8')), 'lxml')
        all_links = soup.find_all(href=re.compile(pattern_trade_links))
        for l in all_links:
            trading_number = ''.join(l.get_text())
            link = l.get("href")
            yield Request(url=link, callback=self.parse_lots,
                          errback=self.errback_httpbin,
                          meta={'trading_number': trading_number})

    def parse_lots(self, response):
        if str(response.status) != '200':
            logger.warning('PROBLEMS WITH CONNECTION')
        else:
            # logger.info(f'We go on trading page --{response.url}--')
            start_request_info = response.xpath(
                get_start_date_request()).get(default=None)
            try:
                check_date_request = return_time_period(start_request_info)
            except:
                check_date_request = '0000-00-00 00:00:00'
                logger.error(
                    f'{response.url}:::START DATE REQUEST IS NOT FOUND')
            if check_date_request < '2017-01-01 00:00:00':
                logger.info(
                    f'Start date request on--{response.url}--less 2017.01.01')
            else:
                loader = SibtopItemLoader(SibtopItem(), response=response)
                loader.add_value('data_origin', main_url_sib)
                loader.add_value('trading_id', ''.join(
                    trade_id(response.url)).strip())
                loader.add_value('trading_link', ''.join(response.url))
                # loader.add_value('trading_number', response.meta['trading_number'])
                loader.add_xpath('trading_type', trade_type_loc)
                loader.add_xpath('trading_form', trade_type_loc)
                loader.add_value('msg_number', check_msg_number(''.join(response.url),
                                                                response.xpath(msg_number()).get()))
                loader.add_value('case_number', check_case_number(''.join(response.url),
                                                                  response.xpath(get_case_number()).get()))
                loader.add_value('debtor_inn', check_inn(
                    ''.join(response.xpath(get_debitor_inn()).get())))
                loader.add_value('trading_org', check_name(
                    ''.join(response.xpath(get_org_name()).get())))
                loader.add_value('trading_org_inn', check_inn(
                    ''.join(response.xpath(get_org_inn()).get())))
                contacts = {'email': check_email(''.join(response.xpath(get_org_email()).get())),
                            'phone': check_phone(''.join(response.xpath(get_org_phone()).get()))}
                loader.add_value('trading_org_contacts', contacts)
                loader.add_value('arbit_manager', check_name(
                    ''.join(response.xpath(get_arbitr_name()).get())))
                loader.add_value('arbit_manager_inn', check_inn(
                    ''.join(response.xpath(get_arbitr_inn()).get())))
                loader.add_value('arbit_manager_org', check_name(
                    ''.join(response.xpath(get_arbitr_org()).get())))
                loader.add_value('status', 'active')
                loader.add_value('lot_id', None)
                loader.add_value('lot_link', None)
                loader.add_value('lot_info', None)
                loader.add_xpath('lot_number', lot_number_loc)
                loader.add_xpath('short_name', short_name)
                loader.add_xpath('property_information',
                                 property_information_loc)
                type_trade = check_trading_type(
                    ''.join(response.xpath(trade_type_loc).get()))
                start_date_request = response.xpath(
                    get_start_date_request()).get()
                end_date_request = response.xpath(
                    get_end_date_requests()).get()
                start_date_trade = response.xpath(
                    get_start_date_trading()).get()
                end_date_trade = response.xpath(get_end_date_trading()).get()
                try:
                    loader.add_value('start_date_requests', return_time_period(
                        ''.join(start_date_request)).strip())
                except:
                    loader.add_value('start_date_requests', None)
                    logger.error(
                        f'{response.url}:::WITHOUT START DATE REQUEST')
                try:
                    loader.add_value('end_date_requests', return_time_period(
                        ''.join(end_date_request)).strip())
                except:
                    loader.add_value('end_date_requests', None)
                    logger.error(f'{response.url}:::WITHOUT END DATE REQUEST')
                try:
                    loader.add_value('start_date_trading', return_time_period(
                        ''.join(start_date_trade)).strip())
                except:
                    loader.add_value('start_date_trading', None)
                    logger.error(
                        f'{response.url}:::WITHOUT START DATE TRADING')
                extra_end_trading = response.xpath(extra_end_trading_loc).get()
                try:
                    if end_date_trade:
                        loader.add_value('end_date_trading', return_time_period(
                            ''.join(end_date_trade)).strip())
                    elif extra_end_trading and str(type_trade) == 'auction' or str(type_trade) == 'competition':
                        try:
                            loader.add_value('end_date_trading', return_time_period(
                                ''.join(extra_end_trading)).strip())
                        except:
                            loader.add_value('end_date_trading', None)
                            logger.error(
                                f'AUCTION WITHOUT DATES __{response.url}')
                    else:
                        loader.add_value('end_date_trading', None)
                except:
                    loader.add_value('end_date_trading', None)
                ###_WORKING_WITH_TABLE_PERIODS_IF_TYPE_IS_OFFER_###
                table_periods = response.xpath(get_table_period())
                if table_periods:
                    full_period = []
                    for tr in table_periods:
                        try:
                            start = tr.xpath('td[1]//text()').get()
                            end = tr.xpath('td[2]//text()').get()
                            price = tr.xpath('td[3]//text()').get()
                            start_date_requests = replaceMultiple(
                                start.strip(), pattern_replace1, ' ')
                            end_date_requests = replaceMultiple(
                                end.strip(), pattern_replace1, ' ')
                            period = {
                                'start_date_requests': return_time_period(start_date_requests),
                                'end_date_requests': return_time_period(end_date_requests),
                                'end_date_trading': return_time_period(end_date_requests),
                                'current_price': make_float(price)

                            }

                        except:
                            continue
                        full_period.append(period)

                    loader.add_value('periods', full_period)
                    start_date_request = response.xpath(
                        lot_table_start_trade).get()
                    end_date_request = response.xpath(
                        lot_table_end_trade).get()
                    start_date_trade = start_date_request
                    end_date_trade = end_date_request
                    try:
                        loader.add_value('start_date_requests', return_time_period(
                            ''.join(start_date_request)).strip())
                    except:
                        logger.error(
                            f'{response.url}:::PERIOD TABLE INCLUDE INVALID DATA')
                    try:
                        loader.add_value('end_date_requests', return_time_period(
                            ''.join(end_date_request)).strip())
                    except:
                        logger.error(
                            f'{response.url}:::PERIOD TABLE INCLUDE INVALID DATA')
                    try:
                        loader.add_value('start_date_trading', return_time_period(
                            ''.join(start_date_trade)).strip())
                    except:
                        logger.error(
                            f'{response.url}:::PERIOD TABLE INCLUDE INVALID DATA')
                    try:
                        loader.add_value('end_date_trading', return_time_period(
                            ''.join(end_date_trade)).strip())
                    except:
                        logger.error(
                            f'{response.url}:::PERIOD TABLE INCLUDE INVALID DATA')
                start_price = response.xpath(start_price_loc).get()
                if 'Начальная цена' in start_price:
                    start_price = response.xpath(start_price_loc).extract()
                    start_price = start_price[1]
                if 'Информация о снижении цены' in start_price:
                    start_price = response.xpath(start_price_loc).extract()
                    if len(start_price) == 2:
                        start_price = start_price[1]
                    if len(start_price) == 3:
                        start_price = start_price[2]
                step_price = response.xpath(step_price_loc).get()
                if start_price:
                    try:
                        loader.add_value(
                            'start_price', make_float(start_price))
                    except:
                        logger.error(
                            f'{response.url}:: START PRICE is INVALID')
                # _need_to_fix_not critical__##
                if 'Начальная цена' in step_price:
                    step_price = response.xpath(step_if_bug).extract()
                    step_price = step_price[0]
                if step_price and (type_trade == 'auction' or type_trade == 'competition'):
                    try:
                        loader.add_value(
                            'step_price', make_float(''.join(step_price)))
                    except:
                        logger.error(f'{response.url}:: STEP PRICE is INVALID')

                files = self.download_trading_files(response)
                extra_files = {'lot': list()}
                total_files = dict(
                    chain(
                        files.items(),
                        extra_files.items()))
                loader.add_value('files', total_files)
                loader.add_value('created_at', return_parse_date())
                return loader.load_item()

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

    def download_trading_files(self, response):
        item = DownlodItem()
        load = DownloadFiles()
        soup = BS(response.text, 'lxml')
        general = list()
        selector_links = soup.select('.doclist a')
        for a in selector_links:
            link_etp = ''.join(a.get('href'))
            original_name = ''.join(a.get_text()).strip()
            original_name = dedent_func(original_name)
            relative_path_server = ''
            if pathlib.Path(original_name).suffix in lst_exet and re.match('.+download/$', link_etp):
                create_dir()
                name_on_server = name_file_on_server(
                    response.url, original_name)
                relative_path_server = name_in_column_files(
                    response.url, original_name)
                load.request_for_download(link_etp, name_on_server)

            general.append({'original_name': original_name,
                            'link': relative_path_server,
                            'link_etp': link_etp})
        item['general'] = general
        return item
