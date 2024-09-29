import logging
import re

from bs4 import BeautifulSoup as BS

from crawler_torgigov.utils.work_with_text_and_number import dedent_func
from ..utils.config import _data_origin
from ..utils.work_with_text_and_number import random_float_value

logger = logging.getLogger(__name__)
MAIN_URL = _data_origin['torgi_gov']


class FinishSection:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(
            str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&'),
            features='lxml')

    def get_search_lot_form(self):
        """:return hall form of search """
        try:
            if form := self.soup.find('form', class_=re.compile('lot-search')):
                return form
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: SEARCH FORM NOT FOUND')

    def get_search_button(self):
        """ get od of search button """
        try:
            search_button = self.soup.find('ins', string=re.compile('^Поиск', re.IGNORECASE))
            _a = search_button.parent
            return _a.get('id')
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: search button not found')

    def get_search_button_link(self, main_link):
        """ get link of button search """
        try:
            search_button = self.soup.find('ins', string=re.compile('^Поиск', re.IGNORECASE))
            _a = search_button.parent
            link_button_search = re.findall(
                r'(\?wicket:interface=:\d+:search_panel:buttonsPanel:search::IActivePageBehaviorListener:\d+:&wicket:ignoreIfNotActive=true).+',
                str(_a).replace('&amp;', '&'))
            return main_link + ''.join(link_button_search) + '&random=' + random_float_value()
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: INVALID DATA GETTING SEARCH BUTTON LINK')

    def link_of_extended_button(self):
        """ :return tag <a> """
        try:
            extended_search = self.soup.find('ins', string=re.compile('Расширенный поиск', re.IGNORECASE))
            # link of extended button
            _a = extended_search.parent
            return _a
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: TAG <a> of search form was not found')

    def get_id_form(self):
        """ get id of form search to show extend form"""
        try:
            _a = self.link_of_extended_button()
            _id = _a.get('id')
            return _id
        except Exception as e:
            logger.error(f'{self.response.url} :: {e} :: ID SEARCH FORM WAS NOT FOUND')
            with open('search_form_finished.txt', 'w') as f:
                f.write(self.response.text)
            return None

    def get_hidden_input(self):
        """ get hidden name of tag input for param data """
        try:
            hidden = self.get_search_lot_form().find('input', type='hidden')
            return hidden.get('name')
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: HIDDEN INPUT NOT FOUND')

    def get_id_field_counrty(self):
        """ :return id of selected field -> country """
        try:
            country_id = self.soup.find('select', {'name': 'extended:country'}).get('id')
            return country_id
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA COUNTRY FIELD ID {e}')

    def link_for_extend_form(self, main_link):
        """ return link for openning extended form """
        try:
            _a = self.link_of_extended_button()
            link = ''.join(re.findall(r'\?wicket:interface=.+IfNotActive=true', str(_a))).replace('&amp;', '&')
            return main_link + link + '&random=' + random_float_value()
        except Exception as ex:
            logger.error(f'{self.response.url} :: {ex} :: ERROR compeleting url for extend form')

    def get_organizer_link(self, main_link, resp_text):
        """ get link for intermidate request with organizer form """
        try:
            soup = BS(str(resp_text), features='html.parser')
            text_soup = dedent_func(str(soup).replace('\'', '"'))
            text_soup = re.sub(r'\s', '', text_soup)
            link = re.findall(
                r'(\?wicket:interface=:\d+:search_panel:search_lot_panel:search_form:extended:bidOrganization:bidOrganization::IActivePageBehaviorListener:\d+:-\d+.+=true)',
                text_soup)
            return main_link + ''.join(link) + '&random=' + random_float_value()
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA ORGANIZER LINK {ex}')

    def get_country_link(self, main_link, resp_text):
        """ get link for intermidate request with organizer form """
        try:
            soup = BS(str(resp_text), features='html.parser')
            text_soup = dedent_func(str(soup).replace('\'', '"'))
            text_soup = re.sub(r'\s', '', text_soup)
            link = re.findall(
                r'(\?wicket:interface=:\d+:search_panel:search_lot_panel:search_form:extended:country::IBehaviorListener:.?\d+:.?\d+)',
                text_soup)
            return main_link + ''.join(link) + '&random=' + random_float_value()
        except Exception as ex:
            logger.error(f'{self.response.url} :: INVALID DATA COUNTRY LINK {ex}')

    def get_link_next(self, main_link):
        """ get next pagination page """
        try:
            if next_page := self.soup.find('a', string=re.compile('Вперед', re.IGNORECASE)):
                link = re.findall(
                    r'(\?wicket:interface=:\d+:search_panel:resultTable:list:bottomToolbars:\d+:toolbar:span:navigator:next::IBehaviorListener:\d+:.?\d+)',
                    str(next_page))
                return main_link + ''.join(link) + '&random=' + random_float_value()
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: PAGINATION ERROR ')

    def get_id_link_next(self):
        """ get next pagination page """
        try:
            if next_page := self.soup.find('a', string=re.compile('Вперед', re.IGNORECASE)):
                return next_page.get('id')
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: PAGINATION ID ERROR ')

    def get_links_to_lots(self):
        """ fetch and complete links to lot """
        try:
            links = self.soup.find_all('a', href=re.compile(r'restricted/notification/.+prevPageN=\d+'))
            href_ = [MAIN_URL + h.get('href') for h in links]
            return href_ if len(href_) > 0 else None
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERROR DURRING GETTING LINKS', exc_info=True)

    # Archived Form
    def get_arch_link_form(self, main_link, resp_text):
        """ fetch link for query (srchived section) """
        try:
            soup = BS(str(resp_text), features='html.parser')
            sc = soup.find_all('script', text=re.compile('wicketAjaxGet'))
            sc = sc[0]
            sc = dedent_func(str(sc).replace('\'', '"'))
            sc = re.sub(r'\s', '', sc)
            _var = re.findall(
                r'(\?wicket:interface=:\d+:search_panel:search_lot_panel.+bidOrganization.+IActivePageBehaviorListener:\d+.+Active=true)',
                sc)
            return main_link + ''.join(_var) + '&random=' + random_float_value()
        except Exception as e:
            logger.error(f'{main_link} :: ERROR "get_arch_link_form"\n{e}')

    def modify_country_link_archived(self):
        """ change link manualy for activate country form when section is ARCHIVED """
        res_url = self.response.url
        url_out_put = re.sub(
            r'bidOrganization:bidOrganization::IActivePageBehaviorListener:1:&wicket:ignoreIfNotActive=true',
            'country::IBehaviorListener:0:', res_url)
        return url_out_put
