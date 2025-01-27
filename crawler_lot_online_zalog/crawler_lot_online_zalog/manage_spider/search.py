from bs4 import BeautifulSoup as BS
import re
import logging
from ..utils.post_data import movable_property as mp
from ..utils.post_data import not_movable_property as nmp
from ..utils.post_data import financial_assets as fs
import copy

from ..utils.post_data.financial_assets import finance_sub_agreements_form, finance_sub_securities_form, \
    finance_sub_cesia_form, finance_sub_not_material_form
from ..utils.post_data.movable_property import move_sub_equipment_with_form, move_sub_others_with_form, \
    move_sub_cars_with_form
from ..utils.post_data.not_movable_property import not_move_sub_homes_form, not_move_sub_ground_form, \
    not_move_sub_others_form, not_move_sub_commercial_form

logger = logging.getLogger(__name__)


class SearchData:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    def get_view_state(self):
        """ retrun  javax.faces.ViewState value """
        try:
            view = self.soup.find('input', id='j_id1:javax.faces.ViewState:0')['value']
            return view
        except Exception as ex:
            print(ex)
            logger.error(f'ERROR GETTING FIRST VIEW OF STATE', exc_info=True)
            return None

    def get_view_state_xlm(self, text):
        """ retrun  javax.faces.ViewState value  XML """
        try:
            soup = BS(str(text), features='html.parser')
            viewstate = re.findall(r'.?\d+:.?\d+$', soup.text)
            if re.match(r'^-', viewstate[0]) or re.match(r'^\d', viewstate[0]):
                return viewstate[0].strip()
            elif '>' in viewstate[0]:
                viewstate = re.sub(r'^>', '', viewstate[0])
                return viewstate.strip()
            else:
                return None
        except Exception as e:
            logger.error(f'ERROR GETTING XML VIEW OF STATE\n{e}', exc_info=True)
            return None

    def return_rad_server_time(self):
        try:
            server_time = self.soup.find('input', id='formMain:inputServerTime')['value']
            return server_time
        except Exception as e:
            print(e)
            logger.error('ERROR SERVER TIME')

    @staticmethod
    def list_of_main_category():
        """ :return list of main category """
        return ['movable_property', 'not_movable_property', 'financial_assets']

    def retrun_special_post_data(self, category_name, view_value, server_time):
        """ :return post data according main category """
        try:
            if category_name == 'financial_assets':
                data = copy.deepcopy(fs.finance_main_category)
                data['javax.faces.ViewState'] = view_value
                data['formMain:inputServerTime'] = server_time
                return data
            elif category_name == 'movable_property':
                data = copy.deepcopy(mp.move_main_category)
                data['javax.faces.ViewState'] = view_value
                data['formMain:inputServerTime'] = server_time
                return data
            elif category_name == 'not_movable_property':
                data = copy.deepcopy(nmp.not_move_main_category)
                data['javax.faces.ViewState'] = view_value
                data['formMain:inputServerTime'] = server_time
                return data
        except Exception as ex:
            logger.error(f'{self.response.url} :{ex}: ERROR CHOOSING POST DATA FOR MAIN CATEGORY')

    def choose_correct_subcat_data(self, category_name, subcategory_name):
        """ return subcategory param data """
        if category_name == 'financial_assets':
            if subcategory_name == 'agreements':
                return fs.finance_sub_agreements_form
            elif subcategory_name == 'material':
                return fs.finance_sub_not_material_form
            elif subcategory_name == 'securities':
                return fs.finance_sub_securities_form
            elif subcategory_name == 'cesia':
                return fs.finance_sub_cesia_form

        elif category_name == 'movable_property':
            if subcategory_name == 'equipment':
                return mp.move_sub_equipment_with_form
            elif subcategory_name == 'others':
                return mp.move_sub_others_with_form
            elif subcategory_name == 'cars':
                return mp.move_sub_cars_with_form

        elif category_name == 'not_movable_property':
            if subcategory_name == 'homes':
                return nmp.not_move_sub_homes_form
            elif subcategory_name == 'ground':
                return nmp.not_move_sub_ground_form
            elif subcategory_name == 'others':
                return nmp.not_move_sub_others_form
            elif subcategory_name == 'commercial':
                return nmp.not_move_sub_commercial_form

    def get_trading_links(self):
        """ return set with unique links  """
        try:
            links = self.soup.find_all(href=re.compile(r'auctionLotProperty.xhtml\?parm=lot'))
            links = set([l.get('href') for l in links])
            return links
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA DURING FETCHING TRADING LINKS {e}', exc_info=True)

    def get_next_button(self):
        """ :return button (true) if exists or None if not exists """
        button = self.soup.find('a', id='formMain:clNext')
        if button:
            return button
        else:
            return None
