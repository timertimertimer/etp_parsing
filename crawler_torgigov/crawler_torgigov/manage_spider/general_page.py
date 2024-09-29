import logging
import re

from bs4 import BeautifulSoup as BS

from crawler_torgigov.utils.work_with_text_and_number import random_float_value
from .finished_section import MAIN_URL
from ..utils.check_inn_email_etc import CheckIfCorrectContactInfo
from ..utils.working_with_time import format_time

logger = logging.getLogger(__name__)


class GeneralPage:

    def __init__(self, response_):
        self.response = response_
        self.check = CheckIfCorrectContactInfo()
        self.soup = BS(
            str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&'),
            features='lxml')

    def get_organizer_name(self, url_lot):
        """ return organizer name """
        try:
            organizer = self.soup.find('label', string=re.compile('Организатор торгов:', re.IGNORECASE))
            organizer = organizer.findNext('td').get_text().strip()
            if len(organizer) > 3:
                return organizer
            else:
                logger.error(f'{url_lot} :: INVALID DATA ORGANIZER NAME')
                return None
        except Exception as e:
            with open(f'get_organizer_name.txt', 'w') as f:
                f.write(self.response.text)
            logger.error(f'{url_lot} :{e}: ERROR ORGANIZER NAME', exc_info=True)

    def get_org_email(self, url_lot):
        """ :return organizer email or empty string """
        try:
            email = self.soup.find('label', string=re.compile('E-Mail:', re.IGNORECASE))
            email = email.findNext('td').get_text().strip()
            if len(email) > 3:
                return self.check.check_email(email)
            else:
                logger.error(f'{url_lot} :: INVALID DATA ORGANIZER EMAIL')
        except Exception as e:
            logger.error(f'{url_lot} :{e}: ERROR ORANIZER EMAIL', exc_info=True)
            with open(f'get_org_email.txt', 'w') as f:
                f.write(self.response.text)
            return ''

    def get_org_phone(self, url_lot):
        """ :return organizer email or empty string """
        try:
            phone = self.soup.find('label', string=re.compile('Телефон:', re.IGNORECASE))
            phone = phone.findNext('td').get_text().strip()
            if len(phone) > 3:
                return self.check.check_phone(phone)
            else:
                logger.error(f'{url_lot} :: INVALID DATA ORGANIZER PHONE')
        except Exception as e:
            logger.error(f'{url_lot} :{e}: ERROR ORANIZER PHONE')
            return ''

    def get_organizer_contacts(self,url_lot):
        """ return dict with organizer email and phone """
        return {'email': self.get_org_email(url_lot), 'phone': self.get_org_phone(url_lot)}

    def get_address_index(self, url_lot):
        """ return index of address d1"""
        try:
            index_ = self.soup.find('label', string=re.compile('Адрес:', re.IGNORECASE))
            index_ = index_.findNext('td').get_text().strip()
            if len(index_) > 3:
                match_ = re.sub(r',$', '', ''.join(re.findall(r'^\d{5,8},?', index_)))
                return match_
        except Exception as e:
            logger.error(f'{url_lot} :{e}: ERROR ADDRESS INDEX', exc_info=True)
            with open(f'get_address_index.txt', 'w') as f:
                f.write(self.response.text)
            return ''

    def start_date_request_bankrot(self, url_lot):
        """ return start date request  """
        try:
            start = self.soup.find('label', string=re.compile('Дата начала подачи заявок:', re.IGNORECASE))
            start_2 = self.soup.find('label', string=re.compile('Дата и время начала подачи заявок:', re.IGNORECASE))
            if start is None:
                start = start_2
            if start:
                start = start.findNext('td').get_text().strip()
                if len(start) > 7:
                    return format_time(start)
        except Exception as e:
            logger.error(f'{url_lot} :{e}: ERROR START DATE REQUEST')
            with open(f'start_date_request_bankrot.txt', 'w') as f:
                f.write(self.soup.text)
            return None

    def end_date_request_bankrot(self, url_lot):
        """ return end date request bankrot section """
        try:
            end = self.soup.find('label', string=re.compile('Дата окончания подачи заявок:', re.IGNORECASE))
            end_2 = self.soup.find('label', string=re.compile('Дата и время окончания подачи заявок:', re.IGNORECASE))
            if end is None:
                end = end_2
            end = end.findNext('td').get_text().strip()
            if len(end) > 7:
                return format_time(end)
            else:
                logger.error(f'{url_lot} :: INVALID END DATE REQUEST')
        except Exception as e:
            logger.error(f'{url_lot} :{e}: ERROR END DATE REQUEST', exc_info=True)
            return ''

    def start_date_trading_bankrot(self, url_lot, trading_type):
        """ return start date request  """
        try:
            start = self.soup.find('label', string=re.compile('Дата и время проведения аукциона:', re.IGNORECASE))
            start2 = self.soup.find('label', string=re.compile('Дата и время вскрытия конвертов:', re.IGNORECASE))
            start3 = self.soup.find('label', string=re.compile('Дата и время проведения торгов:', re.IGNORECASE))
            start4 = self.soup.find('label', string=re.compile('Дата рассмотрения заявок:', re.IGNORECASE))
            if trading_type == 'auction':
                if start is None and start2 is not None:
                    start = start2
                if start is None and start3 is not None:
                    start = start3
                if start is None and start4 is not None:
                    start = start4
                if start:
                    start = start.findNext('td')
                    start = start.get_text().strip()
                    if len(start) > 7:
                        return format_time(start)
            elif trading_type == 'offer':
                if start is None and start3 is not None:
                    start = start3
                if start is None and start2 is not None:
                    start = start2
                if start is None and start4 is not None:
                    start = start4
                if start:
                    start = start.findNext('td')
                    start = start.get_text().strip()
                    if len(start) > 7:
                        return format_time(start)
            elif trading_type == 'competition':
                if start is None and start4 is not None:
                    start = start4
                if start is None and start3 is not None:
                    start = start3
                if start is None and start2 is not None:
                    start = start2
                if start:
                    start = start.findNext('td')
                    start = start.get_text().strip()
                    if len(start) > 7:
                        return format_time(start)
        except Exception as e:
            logger.error(f'{url_lot} :{e}: ERROR START DATE TRADING', exc_info=True)
            return ''

    def get_document_link(self):
        """ get document link for do request to document tab """

    def get_a_document_page(self, url_lot):
        """get link to document page ( tag a of tab) """
        document_page = self.soup.find_all('a', string=re.compile(r'\s?^Документы', re.IGNORECASE))
        if len(document_page) > 0:
            return document_page
        else:
            logger.error(f'{url_lot} :: ERROR TAB TO DOCUMENT PAGE NOT FOUND')
            return None

    def get_id_download_page(self, url_lot):
        """ fetch id of traing page tab """
        if document_page := self.get_a_document_page(url_lot):
            if isinstance(document_page, list):
                if len(document_page) > 1:
                    document_page = document_page[0].split()
                for x in document_page:
                    if x := x.get('id'):
                        return x
                    else:
                        logger.error(f'{url_lot} :: ERROR GETTING ID TAB DOCUMENT PAGE')
                        return None

    def get_link_to_document_page(self, url_lot):
        """ after get tag <a> fetch using regular exp link to trading page """
        if document_page := self.get_a_document_page(url_lot):
            if isinstance(document_page, list):
                if len(document_page) > 1:
                    document_page = document_page[0].split()
                for x in document_page:
                    string = (x['onclick'])
                    search_str = re.findall(r'\?wicket:interface=:\d+.+link::IBehaviorListener:\d+:.?\d+', string)
                    return MAIN_URL + ''.join(search_str) + '&random=' + random_float_value()
