import re

from bs4 import BeautifulSoup as BS

from general_utils import UrlConfig, dedent_func, format_time
from ..locators.serp_locator import LocatorSerp
from ..locators.competition_locator import CompetLocator
import logging

logger = logging.getLogger(__name__)


class CompetitionPage:

    def __init__(self, _response):
        self.response = _response
        self.loc = LocatorSerp
        self.loc_comp = CompetLocator
        self.soup = (
            BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'), features='lxml')
        )

    def get_trading_number_comp(self):
        try:
            legend = self.response.xpath(self.loc_comp.trading_num_loc).get()
            if legend:
                legend = BS(str(legend), features='lxml').get_text()
                legend = ''.join(re.findall(r'\d+', legend))
                return legend
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR TRADING NUMBER\n{e}', exc_info=True)

    @property
    def msg_number(self):
        msg = self.response.xpath(self.loc_comp.msg_number_loc).get()
        if msg:
            msg = BS(str(msg), features='lxml').get_text()
            return ' '.join(re.findall(r'\d{6,8}', dedent_func(msg)))

    def trading_form(self):
        try:
            form = self.response.xpath(self.loc_comp.trading_form_loc).get()
            if form:
                form = BS(str(form), features='lxml').get_text().lower()
                if 'открытая' == form:
                    return 'open'
                elif 'закрытая' == form:
                    return 'closed'
                else:
                    logger.error(f'{self.response.url} :: ERROR TRADING FORM')
        except Exception as e:
            logger.error(f'{self.response.url} :: TRDING TYPE ERROR')

    def start_date_request(self):
        try:
            start = self.response.xpath(self.loc_comp.start_date_request_loc).get()
            if start:
                start = dedent_func(BS(str(start), features='lxml').get_text())
                return format_time(start.strip())
            else:
                logger.error(f'{self.response.url} :: START DATE REQUEST ERROR AUCTION(COMPETITION)')
        except Exception as e:
            logger.error(f'{self.response.url} :: START DATE REQUEST ERROR AUCTION(COMPETITION)::{e}')

    def end_date_request(self):
        try:
            end = self.response.xpath(self.loc_comp.end_date_request_loc).get()
            if end:
                end = dedent_func(BS(str(end), features='lxml').get_text())
                return format_time(end.strip())
            else:
                logger.error(f'{self.response.url} :: end DATE REQUEST ERROR AUCTION(COMPETITION)')
        except Exception as e:
            logger.error(f'{self.response.url} :: end DATE REQUEST ERROR AUCTION(COMPETITION)::{e}')

    def start_date_trading(self):
        try:
            start = self.response.xpath(self.loc_comp.start_date_trading_loc).get()
            if start:
                start = dedent_func(BS(str(start), features='lxml').get_text())
                return format_time(start.strip())
            elif extra_start := self.response.xpath(self.loc_comp.extra_start_date_trading).get():
                extra_start = dedent_func(BS(str(extra_start), features='lxml').get_text())
                return format_time(extra_start.strip())
            elif start_utender := self.response.xpath(self.loc_comp.start_date_trading_utender_loc).get():
                start_utender = dedent_func(BS(str(start_utender), features='lxml').get_text())
                return format_time(start_utender.strip())
            else:
                logger.error(f'{self.response.url} :: START DATE TRADING ERROR (COMPETITION)')
        except Exception as e:
            logger.error(f'{self.response.url} :: START DATE TRADING ERROR (COMPETITION)::{e}')


