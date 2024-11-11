import re

from bs4 import BeautifulSoup as BS
from ..locators.serp_locator import LocatorSerp
from ..locators.competition_locator import CompetLocator
from ..utils.code_for_edit_and_format.working_with_url import UrlConfig
from ..utils.code_for_edit_and_format.work_with_text_and_number import dedent_func
from ..utils.code_for_edit_and_format.check_inn_email_phone import CheckIfCorrectContactInfo
import logging
from ..utils.code_for_edit_and_format.working_with_time import format_time_auction

logger = logging.getLogger(__name__)


class CompetitionPage:
    """ fetch info from serp (infjrmation after request - current page, next page, links to trading page """

    def __init__(self, _response):
        self.response = _response
        self.loc = LocatorSerp
        self.loc_comp = CompetLocator
        self.check = CheckIfCorrectContactInfo()
        self.url = UrlConfig()
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_trading_number_comp(self):
        """ :return trading number for offer"""
        try:
            legend = self.response.xpath(self.loc_comp.trading_num_loc).get()
            if legend:
                legend = BS(str(legend), features='lxml').get_text()
                legend = ''.join(re.findall(r'\d+', legend))
                return legend
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR TRADING NUMBER\n{e}', exc_info=True)

    def get_lot_link(self, lot_number: str, data_origin) -> str or None:
        """:return table with lots number and link (str(html))"""
        try:
            legend = self.response.xpath(self.loc_comp.lot_table).get()
            if legend:
                legend = BS(str(legend), features='lxml')
                table = legend.find('legend', string='Лоты публичного предложения').parent
                # choose type of trade
                if table and len(table) > 0:
                    link = table.find('a', string=lot_number)
                    if link:
                        link = link.get('href')
                        return self.url.url_join(data_origin, link)
        except Exception as e:
            logger.critical(f'{self.response.url} :{e}: INVALID DATA LOT TABLE', exc_info=True)
            return None

    def get_property_info(self):
        """ return short name """
        property_info = self.response.xpath(self.loc_comp.property_info_loc).get()
        if property_info:
            property_info = dedent_func(BS(str(property_info), features='lxml').get_text())
            return property_info.strip()

    @property
    def msg_number(self):
        """ :return message number """
        msg = self.response.xpath(self.loc_comp.msg_number_loc).get()
        if msg:
            msg = BS(str(msg), features='lxml').get_text()
            return ' '.join(re.findall(r'\d{6,8}', dedent_func(msg)))

    def trading_form(self):
        """return trading form"""
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

    def get_lot_link(self, lot_number: str, _data_origin) -> str or None:
        """:return table with lots number and link (str(html))"""
        try:
            legend = self.response.xpath(self.loc_comp.lot_table).get()
            if legend:
                legend = BS(str(legend), features='lxml')
                table = legend.find('legend', string='Лоты конкурса').parent
                # choose type of trade
                if table and len(table) > 0:
                    link = table.find('a', string=lot_number)
                    if link:
                        link = link.get('href')
                        return self.url.url_join(_data_origin, link)
        except Exception as e:
            logger.critical(f'{self.response.url} :{e}: INVALID DATA LOT TABLE', exc_info=True)
            return None

    def get_property_info(self):
        """ return short name """
        property_info = self.response.xpath(self.loc_comp.property_info_loc).get()
        if property_info:
            property_info = dedent_func(BS(str(property_info), features='lxml').get_text())
            return property_info.strip()

    def start_date_request(self):
        """ :return start date request auction """
        try:
            start = self.response.xpath(self.loc_comp.start_date_request_loc).get()
            if start:
                start = dedent_func(BS(str(start), features='lxml').get_text())
                return format_time_auction(start.strip())
            else:
                logger.error(f'{self.response.url} :: START DATE REQUEST ERROR AUCTION(COMPETITION)')
        except Exception as e:
            logger.error(f'{self.response.url} :: START DATE REQUEST ERROR AUCTION(COMPETITION)::{e}')

    def end_date_request(self):
        """ :return start date request auction """
        try:
            end = self.response.xpath(self.loc_comp.end_date_request_loc).get()
            if end:
                end = dedent_func(BS(str(end), features='lxml').get_text())
                return format_time_auction(end.strip())
            else:
                logger.error(f'{self.response.url} :: end DATE REQUEST ERROR AUCTION(COMPETITION)')
        except Exception as e:
            logger.error(f'{self.response.url} :: end DATE REQUEST ERROR AUCTION(COMPETITION)::{e}')

    def start_date_trading(self):
        """ :return start date request auction """
        try:
            start = self.response.xpath(self.loc_comp.start_date_trading_loc).get()
            if start:
                start = dedent_func(BS(str(start), features='lxml').get_text())
                return format_time_auction(start.strip())
            elif extra_start := self.response.xpath(self.loc_comp.extra_start_date_trading).get():
                extra_start = dedent_func(BS(str(extra_start), features='lxml').get_text())
                return format_time_auction(extra_start.strip())
            else:
                logger.error(f'{self.response.url} :: START DATE TRADING ERROR AUCTION(COMPETITION)')
        except Exception as e:
            logger.error(f'{self.response.url} :: START DATE TRADING ERROR AUCTION(COMPETITION)::{e}')


