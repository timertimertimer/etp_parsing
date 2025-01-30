# -*- coding: utf-8 -*-
import logging
import pandas as pd
import numpy as np

from bs4 import BeautifulSoup as BS

from ..locators_and_attributes.locators_attributes import Offer
from ..utils.config import data_origin_url
from ..utils.working_with_url import UrlConfig
from ..utils.working_with_time import format_time
from ..utils.work_with_text_and_number import *
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo

logger = logging.getLogger(__name__)


class OfferSpider:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')
        self.url = UrlConfig()
        self.loc = Offer
        self.check = CheckIfCorrectContactInfo()

    def get_post_data_values(self, tag_html: str, post_argument: str) -> str or None:
        """
        :arg tag_html
        :arg post_argument
        :return value
        P.S. work only with id
         """
        try:
            tag_html = self.soup.find(tag_html, id=post_argument)
            if tag_html:
                tag_html = tag_html['value']
                return tag_html
            else:
                return ''
        except Exception as e:
            logger.error(f' :: Exeption during fetching tag {tag_html} :: {e} ')
            return ''

    def get_ajax_and_token(self):
        """get value from script tag for post data field 'ctl00_ToolkitScriptManager1_HiddenField'"""
        try:
            ajax_control = ''.join(
                [s.get('src') for s in self.soup.find_all('script') if 'AjaxControlToolkit' in str(s.get('src'))])
            if ajax_control and len(ajax_control) > 0:
                a = ''.join(re.findall(r'TSM_CombinedScripts_=(.*)$', ajax_control))
                return self.url.make_url_unquote(a)
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR GETTING ctl00_ToolkitScriptManager1_HiddenField value ::\n{e}')
            return ''

    @property
    def trade_link_serp(self) -> set:
        """gettting links to the trading page and return set"""
        try:
            link_set = set()
            list_tag_links = self.response.xpath(self.loc.trading_links_loc).getall()
            if list_tag_links and len(list_tag_links) > 0:
                for link in list_tag_links:
                    if link and re.match('/public.+aspx.+\d+$', link):
                        link_set.add(self.url.url_join(data_origin_url, link))
                return link_set
        except:
            logger.error(f'{self.response.url} :: ERROR DURING GETTING LINKS TO TRADING PAGE')
            return set()

    def get_total_pages(self, page, date):
        """ return number of the last available page """
        try:
            select = self.soup.find('select', title='Выбор номера страницы').find_all_next('option')
            if len(select) > 0:
                number = select[-1].get_text()
                if number and len(number) <= 6:
                    if re.match(r'^\d+$', number):
                        return int(number)
            else:
                return 0
        except ValueError as e:
            logger.error(f'{e} :: {self.response.url} :: ERROR on page {page} :: time {date} ')
            return None

    @property
    def get_trading_number(self) -> str or None:
        """ return trading number """
        trade_number = self.response.xpath(self.loc.trading_number_loc).get()
        if trade_number and len(trade_number) > 0:
            t = dedent_func(BS(str(trade_number), features='lxml').get_text()).strip()
            if len(t) > 0 and re.match(r'\d{1,12}', t):
                return self.check.check_number(t)
        else:
            logger.warning(f'{self.response.url} :: INVALID DATA OR IS MISSING TARDING NUMBER')
            return None

    @property
    def get_trading_type(self):
        """ return trading type """
        trading_type = self.response.xpath(self.loc.trading_type_loc).get()
        if trading_type and len(trading_type) > 0:
            type_ = dedent_func(BS(str(trading_type), features='lxml').get_text()).strip()
            if type_ in ['Публичное предложение', 'Открытое публичное предложение', 'Закрытое публичное предложение']:
                return 'offer'
            else:
                logger.error(f'{self.response.url} :: INVALID DATA TRADING TYPE')
                return 'offer'

    def get_status(self):
        """ return status """
        trading_status = self.response.xpath(self.loc.trading_status_loc).get()
        if trading_status and len(trading_status) > 0:
            status = dedent_func(BS(str(trading_status), features='lxml').get_text()).strip().lower()
            if status == 'прием заявок':
                return 'active'
            elif status == 'торги объявлены':
                return 'pending'
            else:
                return 'ended'

    @property
    def get_trading_form(self):
        """ return trading form """
        trading_type = self.response.xpath(self.loc.trading_type_loc).get()
        if trading_type and len(trading_type) > 0:
            type_ = dedent_func(BS(str(trading_type), features='lxml').get_text()).strip()
            if type_ in ['Аукцион', 'Открытый аукцион', 'Конкурс', 'Открытый конкурс', 'Публичное предложение',
                         'Открытое публичное предложение']:
                return 'open'
            else:
                return 'closed'

    @property
    def get_trading_org_name(self):
        """determine the organizer(company or person)"""
        try:
            if_company = self.response.xpath(self.loc.list_of_company_id).getall()
            person = self.response.xpath(self.loc.list_person_info_id).getall()
            if len(if_company) > 0:
                for tr in if_company:
                    td = BS(str(tr), features='lxml').find_all('td')
                    if len(td) == 2:
                        if 'олное наименование организаци' in dedent_func(td[0].get_text()):
                            return dedent_func(td[1].get_text())
            elif len(person) > 0:
                lastname, fistname, middlename = '', '', ''
                for tr in person:
                    td = BS(str(tr), features='lxml').find_all('td')
                    if len(td) == 2:
                        if 'амили' in dedent_func(td[0].get_text()):
                            lastname = dedent_func(td[1].get_text())
                        if 'Имя' in dedent_func(td[0].get_text()):
                            fistname = dedent_func(td[1].get_text())
                        if 'тчество' in dedent_func(td[0].get_text()):
                            middlename = dedent_func(td[1].get_text())
                return lastname + ' ' + fistname + ' ' + middlename
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR GETTING ORGANIZER COMPANY NAME - {e}', exc_info=True)
            return None

    @property
    def get_org_inn(self) -> str or None:
        """:return trading organizer inn """
        try:
            if_company = self.response.xpath(self.loc.list_of_company_id).getall()
            person = self.response.xpath(self.loc.list_person_info_id).getall()
            if len(if_company) > 0:
                for tr in if_company:
                    td = BS(str(tr), features='lxml').find_all('td')
                    if len(td) == 2:
                        if 'ИНН' in dedent_func(td[0].get_text()):
                            return self.check.check_inn(dedent_func(td[1].get_text()))
            elif len(person) > 0:
                for tr in person:
                    td = BS(str(tr), features='lxml').find_all('td')
                    if len(td) == 2:
                        if 'ИНН' in dedent_func(td[0].get_text()):
                            return self.check.check_inn(dedent_func(td[1].get_text()))

        except Exception as e:
            logger.error(f'{self.response.url} :: {e}\n INVALID DATA ORG INN')
            return None

    @property
    def get_email_org(self):
        """:return organizer email"""
        try:
            email = self.soup.find(id=self.loc.org_email_loc).get_text()
            if email:
                return self.check.check_email(dedent_func(email))
            else:
                return ''
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA EMAIL ORG\{e}')

    @property
    def get_phone_org(self):
        """:return """
        try:
            phone_ = self.response.xpath(self.loc.phone_org_loc).get()
            if phone_:
                phone = BS(str(phone_), features='lxml').get_text()
                return self.check.check_phone(dedent_func(phone))
            else:
                return ''
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA EMAIL ORG\{e}')

    @property
    def org_contacts(self):
        """:return organizer cantacts"""
        return {'email': self.get_email_org, 'phone': self.get_phone_org}

    @property
    def get_msg(self):
        """:return message number FEDRESURS"""
        msg = self.soup.find(id='ctl00_cph1_trIDEFRSB')
        if msg:
            msg_ = msg.find_next('td')
            if msg_:
                msg__ = msg_.find_next('td')
                if msg__:
                    msg = dedent_func(msg__.get_text())
                return ' '.join(re.findall(r'\d{6,9}', msg))

    @property
    def get_case_number(self):
        """ return case number"""
        case = self.soup.find(id='ctl00_cph1_trDealNum')
        if case:
            case_ = case.find_next('td')
            if case_:
                case__ = case_.find_next('td')
                if case__:
                    case = dedent_func(case__.get_text())
                    if len(case) > 4:
                        return self.check.check_case_number(case)

    @property
    def get_debtor_inn(self):
        """:return debtor inn"""
        try:
            debtor = self.response.xpath(self.loc.list_debtor_id).getall()
            if len(debtor) > 0:
                for tr in debtor:
                    td = BS(str(tr), features='lxml').find_all('td')
                    if len(td) == 2:
                        if 'ИНН' in dedent_func(td[0].get_text()):
                            return self.check.check_inn(dedent_func(td[1].get_text()))
        except:
            logger.error(f'{self.response.url} :: INVALID DATA dbtor inn')

    @property
    def address(self):
        try:
            address = self.response.xpath(self.loc.sud_loc).get()
            if address:
                address = BS(str(address), features='lxml').find('span', id='ctl00_cph1_lDealArbJud')
                if address:
                    return dedent_func(' '.join(address.get_text(strip=True).split()))
        except:
            logger.error(f'{self.response.url} :: INVALID DATA sud address')

    @property
    def get_arbitr_name(self):
        """ :return arbitr name"""
        try:
            arbitr = self.response.xpath(self.loc.list_arbitr_id).getall()
            lastname, fistname, middlename = '', '', ''
            for tr in arbitr:
                td = BS(str(tr), features='lxml').find_all('td')
                if len(td) == 2:
                    if 'Не требуется для данных торгов' not in td[1].get_text():
                        if 'амили' in dedent_func(td[0].get_text()):
                            lastname = dedent_func(td[1].get_text())
                        if 'Имя' in dedent_func(td[0].get_text()):
                            fistname = dedent_func(td[1].get_text())
                        if 'тчество' in dedent_func(td[0].get_text()):
                            middlename = dedent_func(td[1].get_text())
                    else:
                        return None
            return lastname + ' ' + fistname + ' ' + middlename
        except:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR NAME')

    @property
    def get_arbitr_inn(self):
        """:return debtor inn"""
        try:
            arbitr = self.response.xpath(self.loc.list_arbitr_id).getall()
            if len(arbitr) > 0:
                for tr in arbitr:
                    td = BS(str(tr), features='lxml').find_all('td')
                    if len(td) == 2:
                        if 'ИНН' in dedent_func(td[0].get_text()):
                            return self.check.check_inn(dedent_func(td[1].get_text()).strip())
        except:
            logger.error(f'{self.response.url} :: INVALID DATA arbitr inn')

    @property
    def get_arbitr_org(self):
        """:return arbitr manager org"""
        try:
            arbitr_org = self.response.xpath(self.loc.list_arbitr_id).getall()
            if len(arbitr_org) > 0:
                for tr in arbitr_org:
                    td = BS(str(tr), features='lxml').find_all('td')
                    if len(td) == 2:
                        if 'организации арбитражных управляющ' in dedent_func(td[0].get_text().strip()):
                            org = dedent_func(td[1].get_text())
                            if 'Не требуется для данных торгов' not in org:
                                if '(' in org:
                                    return ''.join(re.split(r'\(', org, maxsplit=1)[0])
                                else:
                                    return org
        except:
            logger.error(f'{self.response.url} :: INVALID DATA ARBITR COMPANY')

    @delete_extra_symbols
    @cut_lot_number
    def get_short_name(self):
        """:return short name of lot"""
        try:
            short_name = self.soup.find(id=self.loc.short_name_id_loc)
            if short_name:
                return dedent_func(short_name.get_text())
        except:
            logger.error(f'{self.response.url}')

    @delete_extra_symbols
    @cut_lot_number
    def get_lot_info(self):
        """:return short name of lot"""
        try:
            lot_info = self.soup.find(id=self.loc.lot_info_id_loc)
            if lot_info:
                return dedent_func(lot_info.get_text())
        except:
            logger.error(f'{self.response.url}:: INVALID DATA LOT INFO')

    @get_lot_number
    def get_lot_number_(self):
        """:return short name of lot"""
        try:
            short_name = self.soup.find(id=self.loc.short_name_id_loc)
            if short_name:
                return dedent_func(short_name.get_text())
        except:
            logger.error(f'{self.response.url}')

    def get_property_info(self):
        """:return short name of lot"""
        try:
            property_ = self.soup.find(id=self.loc.property_info_if_loc)
            if property_:
                return dedent_func(property_.get_text())
        except:
            logger.error(f'{self.response.url}:: INVALID DATA LOT INFO')

    # WORKING WITH PERIOD TABLE
    @property
    def get_period_table(self) -> list or None:
        """:return list with  periods table tag"""
        try:
            lst_table = self.response.xpath(self.loc.period_table).getall()
            if lst_table and len(lst_table) > 0:
                return lst_table
            else:
                logger.error(f'{self.response.url} :: PERIOD TABLE WAS NOT FOUND')
        except Exception as e:
            logger.error(f'{e}')
            return None

    @property
    def clean_period_table(self):
        """filter all extra information from table(periods). Return list to lates conver to dataframe"""
        try:
            if self.get_period_table:
                table = BS(self.get_period_table[0], features='lxml')
                new_lst = list()
                # list with ignoring words
                exc_w = ['рафик снижения цены', 'ачало периода действи', 'онец периода действи']
                for tr in table.find_all('tr'):
                    text_tr = tr.get_text()
                    if (exc_w[0] not in text_tr) and (exc_w[1] not in text_tr) and (exc_w[2] not in text_tr):
                        if len(text_tr) > 0:
                            new_lst.append(BS(str(tr), features='lxml'))
                return new_lst
        except Exception as e:
            logger.error(f'{e} :: ERROR FORMATING NEW LIST WITH TABLE PERIOD DATA T ODATA FRAME')

    @property
    def create_df_period(self):
        """return DATA FRAME with periods"""
        try:
            lst_df = list()
            for d in self.clean_period_table:
                td = [t.get_text() for t in d.find_all('td')]
                lst_df.append(td)
            df2 = pd.DataFrame(np.array(lst_df),
                               columns=['seq', 'start_date', 'end_date', 'price'])
            return df2
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR CREATE DATA FRAME(PERIOD TABLE) :: {e}')
            return None

    @property
    def get_periods(self):
        """return complete periods in list with dict"""
        df = self.create_df_period

        periods = list()
        for i in range(len(df)):
            start = self.create_df_period.iloc[i]['start_date']
            end = self.create_df_period.iloc[i]['end_date']
            price = self.create_df_period.iloc[i]['price']
            if isinstance(price, str):
                price = ''.join(re.sub(r"\s", "", price)).replace(',', '.')
                price = round(float(price), 2)
            else:
                # if numpy object (but in this case it's not imposible and just in case)
                price = round(float(price), 2)
            period = {
                'start_date_requests': format_time(start),
                'end_date_requests': format_time(end),
                'end_date_trading': format_time(end),
                'current_price': price
            }
            periods.append(period)
        return periods
        # except Exception as e:
        #     logger.error(f'{self.response.url} :: PERIOD TABLE :: {e}', exc_info=True)

    # END WORKING WITH PERIOD TABLE

    @property
    def get_start_date_req(self):
        """ retrun start_date_request """
        try:
            start_date = self.create_df_period.iloc[0]['start_date']
            return format_time(start_date)
        except Exception as e:
            logger.error(f'{self.response.url} :: START DATE REQUEST ERROR - OFFER\n{e}')
            return None

    @property
    def get_start_date_trading(self):
        """ retrun start_date_request """
        return self.get_start_date_req

    @property
    def get_end_date_req(self):
        """ retrun start_date_request """
        try:
            start_date = self.create_df_period.iloc[-1]['end_date']
            return format_time(start_date)
        except Exception as e:
            logger.error(f'{self.response.url} :: START DATE REQUEST ERROR - OFFER\n{e}')
            return None

    @property
    def get_end_date_trading(self):
        """ retrun start_date_request """
        return self.get_end_date_req

    @property
    def get_start_price(self):
        """ return start price offer"""
        try:
            price = self.create_df_period.iloc[0]['price']
            price = ''.join(re.sub(r"\s", "", price)).replace(',', '.')
            return round(float(price), 2)
        except Exception as e:
            logger.error(f'{self.response.url} :: START DATE REQUEST ERROR - OFFER\n{e}')
            return None
