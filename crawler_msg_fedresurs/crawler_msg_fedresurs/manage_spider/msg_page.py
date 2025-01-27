from bs4 import BeautifulSoup as BS
import logging
from ..locators.msg_page_loc import MsgLocator
from ..utils.work_with_text_and_number_cookies import dedent_func
import re
from ..utils.config import public_tender_msg, announce_msg_trade, report_of_valuer, start_link, modified_message_msg
from ..utils.working_with_url import UrlConfig
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo as check

logger = logging.getLogger(__name__)


class MessagePage:

    def __init__(self, response_):
        self.response = response_
        self.url_msg = UrlConfig()
        self.loc = MsgLocator
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    @property
    def get_msg_number(self) -> str:
        """:return msg number"""
        try:
            num = self.response.xpath(self.loc.msg_number_loc).get()
            if num:
                num = BS(str(num), features='lxml').get_text()
                return check.check_number(dedent_func(num))
            else:
                print(self.response.text)
        except Exception as e:
            logger.error(f'{self.response.url} :: Message Number Error {e}')

    def insert_extra_cookies(self, cookies):
        """add cookies to already fetched from response(for making Request to msg page"""
        try:
            if cookies:
                new_value = 'googtrans=/ru/ru'
                cookies = cookies.split(';')
                cookies.insert(2, new_value)
                cookies.insert(3, new_value)
                return '; '.join(cookies)
        except:
            logger.error(f'{self.response.url} :: INVALID COOKIES ADDED FOR MSG PAGE')
            return None

    def get_msg_type(self, m_type):
        """:arg m_type; get type from iteration and check with type on the page"""
        try:
            msg_type = self.soup.find('table').findNext('h1', attrs={'class': 'red_small'}).get_text()
            msg_type = dedent_func(str(msg_type))
            if m_type in msg_type:
                return msg_type
            else:
                logger.error(f'{self.response.url}  -  Message Type doesn\'t match with iteration type')
                return None
        except:
            return None

    def get_publicat_date(self):
        """return publication date"""
        try:
            pub_date = self.response.xpath(self.loc.msg_pub_date_loc).get()
            if pub_date:
                pub_date = BS(str(pub_date), features='lxml').get_text()
                return dedent_func(pub_date)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA publish_date')

    def get_debtor_inn(self):
        """return debtor inn"""
        try:
            inn_ = self.response.xpath(self.loc.msg_deb_inn_loc).get()
            if inn_:
                inn_ = BS(str(inn_), features='lxml').get_text()
                return check.check_inn(dedent_func(inn_))
        except Exception as e:
            logger.warning(f'{self.response.url} :: INVALID DATA debtor_inn\n{e}')
        else:
            return None

    def get_case_number(self):
        """return debtor inn"""
        try:
            case_number = self.response.xpath(self.loc.msg_case_num_loc).get()
            if case_number:
                case_number = BS(str(case_number), features='lxml').get_text()
                return check.check_case_number(dedent_func(case_number.strip()))
        except:
            logger.error(f'{self.response.url} :: INVALID DATA debtor_inn')

    def get_deb_name(self):
        """check who is debtor: person or company"""
        try:
            person = self.response.xpath(self.loc.msg_deb_name).get()
            if person:
                debtor = BS(str(person), features='lxml').get_text()
                return dedent_func(debtor.strip()).title()
            else:
                company = self.response.xpath(self.loc.msg_deb_naimenovanie).get()
                if company:
                    debtor = BS(str(company), features='lxml').get_text()
                    return dedent_func(debtor.strip())
        except:
            logger.error(f'{self.response.url} :: INVALID DATA DEBTOR NAME')
            return None

    def get_debtor_address(self):
        """with extra check who is debtor: person or company"""
        try:
            person = self.response.xpath(self.loc.msg_deb_name).get()
            if person:
                address = self.response.xpath(self.loc.msg_deb_place_add_loc).get()
                address = BS(str(address), features='lxml').get_text()
                return address
            else:
                company = self.response.xpath(self.loc.msg_deb_naimenovanie).get()
                if company:
                    address = self.response.xpath(self.loc.msg_deb_address).get()
                    address = BS(str(address), features='lxml').get_text()
                    return dedent_func(address)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA debtor address')
            return None

    def get_lot_table(self):
        """check if lots table exists if it's true than return it"""
        try:
            table_lot = BS(str(self.soup.find('table', class_='lotInfo')), features='lxml')
            table = table_lot
            if table:
                return table
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA LOTS TABLE\n{e}')
            return None

    @staticmethod
    def save_file_data(original_name, link_fed, link_server=None):
        """save data about file - link on fedresurs and original name. Return dictionary"""
        if original_name:
            original_name = dedent_func(original_name)
        return {'original_name': original_name, 'link': link_server, 'link_fedresurs': link_fed}

    def managed_files(self, msg_type, only_cookies=None):
        """get msg type then according the type download or save only text data or ignore"""
        # load = DownloadFiles()
        try:
            files = self.soup.find('div', class_="files").find_all_next('a')
        except:
            files = None
        files_lst = list()
        if files and len(files) > 0:
            # f_name - file name on server
            f_name = None
            name_at_database = None
            if msg_type in [announce_msg_trade, public_tender_msg, report_of_valuer, modified_message_msg]:
                for f in files:
                    try:
                        o_name = dedent_func(BS(str(f), features='lxml').get_text())
                    except Exception as e:
                        logger.error(f'{self.response.url} :: INVALID DATA FILE NAME\n{e}')
                        o_name = None
                    try:
                        link_fed_ = BS(str(f), features='lxml').find('a').get('href')
                    except:
                        return None
                    if link_fed_:
                        link_fed_ = self.url_msg.url_join(start_link, str(link_fed_) + '&attempt=1')
                    files_lst.append({'original_name': dedent_func(o_name),
                                      'link': link_fed_
                                      })
                    # check if message must be downloaded
                    # if msg_type in report_of_valuer:
                    #     cookie_path = ''.join(re.findall('/Down.+', link_fed_))
                    #     # extra_name_for_file & extra_name are generation 4 digits before file name
                    #     extra_name_for_file = ''.join(re.findall(r'\d', cookie_path))
                    #     if len(extra_name_for_file) > 6:
                    #         extra_name = extra_name_for_file[2:6]
                    #     else:
                    #         extra_name = None
                    #     f_name = load.just_file_name(original_name=o_name, extra=extra_name)
                    #     name_at_database = load.return_files_relative_path(name=f_name)
                    #     load.create_dir()
                    #     load.request_to_download(url=link_fed_, original_name=f_name,
                    #                              referer=self.response.url,
                    #                              cookies=only_cookies,
                    #                              cookie_path=cookie_path)

        return files_lst


class AnnounceStartTrade(MessagePage):
    """inheritance from class that return common info for all messages"""

    def __init__(self, response_):
        super().__init__(response_)

    def get_all_lots(self):
        """ iterate throw lots table and fetch data  """
        table_lot = self.get_lot_table()
        lots = list()
        try:
            for tr in table_lot.find_all('tr'):
                # iterate throw tr but ignore first tr (first tr include th)
                if not tr.find_all('th'):
                    tr_td = tr.find_all('td')
                    # get td with data
                    lot_number = tr_td[0].get_text()
                    lot_name = tr_td[1].get_text()
                    step_price = tr_td[3].get_text()
                    if step_price and re.match(r'\d+.\d+|\d+', str(step_price)):
                        try:
                            if isinstance(step_price, str):
                                if '%' in step_price:
                                    price = ''.join(tr_td[2].get_text()).replace('руб.', '').strip()
                                    price = re.sub(r'\s+', '', price.replace(',', '.'))
                                    price = ''.join(re.findall(r"\d+.\d+|\d+", str(price)))
                                    if price:
                                        step_price = re.sub(r'\s+', '', step_price.replace(',', '.'))
                                        step_price = ''.join(re.findall(r"\d+.\d+|\d+", str(step_price)))
                                        step_price = float(price) * float(step_price) / 100
                                        step_price = round(float(step_price), 2)
                                else:
                                    step_price = re.sub(r'\s+', '', step_price.replace(',', '.'))
                                    step_price = ''.join(re.findall(r"\d+.\d+|\d+", str(step_price)))
                                    step_price = round(float(step_price), 2)
                        except Exception as e:
                            logger.error(f'{self.response.url} :: Price Step Error\n{e}')
                            return None
                    else:
                        step_price = None
                    # split classification by <br> tag if it exists. It does mean that more then 1 category present
                    main_classification = list()
                    classification = re.split(r'<br/?>', ''.join(re.findall(r'<td.*?>(.*?)</td>', str(tr_td[-1]))))
                    for c in classification:
                        if len(c) > 0:
                            main_classification.append(c)
                    if len(main_classification) == 0:
                        stuff_class = tr_td[-1].get_text()
                        main_classification.append(stuff_class)
                    lots.append({'lot_number': lot_number,
                                 'lot_name': dedent_func(lot_name),
                                 'step_price': step_price,
                                 'classification': main_classification})
            return lots
        except Exception as e:
            return logger.error(f'TABLE OF LOTS HAS INVALID DATA\n{e}')


class MsgResultTrade(MessagePage):
    """inheritance from class that return common info for all messages"""

    def __init__(self, response_):
        super().__init__(response_)

    def tendering_message(self):
        """return number of publication of tendering message(announced_message)"""
        try:
            tender_msg = self.response.xpath(self.loc.msg_tenderring).get()
            if tender_msg and len(tender_msg) > 0 and tender_msg != 'None':
                tender = BS(str(tender_msg), features='lxml').get_text()
                tender = ''.join(re.findall(r'\d{5,}', tender))
                if tender and (5 < len(tender) < 9):
                    return tender
                else:
                    logger.error(f'{self.response.url} :: Lenght of publication tender message less then five numbers')
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA PUBLICATION OF TENDER MESSAGE\n{e}')

    def get_all_lots_tender(self):
        """ iterate throw lots table and fetch data  """
        table_lot = self.get_lot_table()
        lots = list()
        try:
            for tr in table_lot.find_all('tr'):
                # iterate throw tr but ignore first tr (first tr include th)
                if not tr.find_all('th'):
                    tr_td = tr.find_all('td')
                    lot_number = tr_td[0].get_text()
                    lot_name = tr_td[1].get_text()
                    # split classification by <br> tag if it exists. It does mean that more then 1 category present
                    main_classification = list()
                    classification = re.split(r'<br/?>', ''.join(re.findall(r'<td.*?>(.*?)</td>', str(tr_td[-1]))))
                    for c in classification:
                        if len(c) > 0:
                            main_classification.append(c)
                    if len(main_classification) == 0:
                        stuff_class = tr_td[-1].get_text()
                        main_classification.append(stuff_class)
                    lots.append({'lot_number': lot_number,
                                 'lot_name': dedent_func(lot_name),
                                 'step_price': None,
                                 'classification': main_classification})
            return lots
        except Exception as e:
            return logger.error(f'TABLE OF LOTS HAS INVALID DATA\n{e}')


class CanceledMsgTrade(MessagePage):

    def __init__(self, response_):
        self.response = response_
        super().__init__(response_)

    def canceled_message(self):
        """return number of canceled message"""
        try:
            canceled_msg = self.response.xpath(self.loc.msg_canceled).get()
            if canceled_msg and len(canceled_msg) > 0 and canceled_msg != 'None':
                cancel = BS(str(canceled_msg), features='lxml').get_text()
                cancel = ''.join(re.findall(r'\d{5,}', cancel))
                if cancel and (5 < len(cancel) < 9):
                    return cancel
                else:
                    logger.error(f'{self.response.url} :: Lenght of publication tender message less then five numbers')
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA  OF cancel MESSAGE\n{e}')


class ChangeTradeProcedure(MessagePage):

    def __init__(self, response_):
        self.response = response_
        super().__init__(response_)

    def changed_message(self):
        """return number of canceled message"""
        try:
            changed_msg = self.response.xpath(self.loc.msg_change_trade_procedure).get()
            if changed_msg and len(changed_msg) > 0 and changed_msg != 'None':
                changed = BS(str(changed_msg), features='lxml').get_text()
                changed = ''.join(re.findall(r'\d{5,}', changed))
                if changed and (5 < len(changed) < 9):
                    return changed
                else:
                    logger.error(f'{self.response.url} :: Lenght of publication tender message less then five numbers')
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA  OF CHANGED MESSAGE\n{e}')
