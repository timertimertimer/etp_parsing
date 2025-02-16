import pathlib
import logging
import re

from general_utils.config import lst_exet_archive, lst_exeption, lst_exet
from general_utils.download import DownloadFiles
from general_utils.models import RequestData
from general_utils.work_with_path_and_dir import FilesDir
from ..locators.trading_page_locator import GeneralInfoLocator
from ..utils.config import data_origin, debtor_link, lot_link, absolute_path, relative_path, host
from ..utils.post_data import post_data_download
from general_utils import (
    dedent_func, replaceMultiple, pattern_replace1,
    what_time_bigger, return_parse_date,
    UrlConfig, format_time
)
from bs4 import BeautifulSoup as BS

logger = logging.getLogger(__name__)


class MainTradingPage:
    """ first page of every lot  """

    def __init__(self, response):
        self.response = response
        self.main_url = re.sub(r'/$', '', data_origin)
        self.soup = BS(
            str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
            features='lxml'
        )

    def get_link_redirect(self):
        """ get link from redirect page """
        try:
            url = self.soup.find('partial-response').find('redirect').get('url')
        except Exception as e:
            return
        if url:
            return UrlConfig.url_join(self.main_url, url)
        else:
            logger.error(f'{self.response.url} :: NO VALUE LINK')
            with open('redirect_page.txt', 'w') as f:
                f.write(self.response.text)

    def get_debtor_info_link(self, url):
        """ return link to debtor info tab """
        param = UrlConfig.return_only_param(url)
        return debtor_link + f'?{param}'

    def get_lot_tab_link(self, url):
        """ return link to lot info tab """
        param = UrlConfig.return_only_param(url)
        return lot_link + f'?{param}'

    def get_trading_number(self):
        """ get trading number from top of the page """
        num = self.response.xpath(GeneralInfoLocator.trading_number_loc).get()
        return num

    @property
    def get_string_trading_type(self):
        """ :return text for getting type and form in another functions """
        label_type_trade = self.response.xpath(GeneralInfoLocator.trading_type_loc).get()
        text = BS(str(label_type_trade), features='lxml')
        text = dedent_func(text.get_text().split('.')[-1].strip())
        return text

    def get_trading_type(self):
        """ :return trading type (5)"""
        _type = self.get_string_trading_type
        offer_type = ('Продажа посредством публичного предложения',)
        auction_type = ('Открытый аукцион с открытой формой подачи предложений',
                        'Открытый аукцион с закрытой формой подачи предложений',)
        competition_type = ('Открытый конкурс с открытой формой подачи предложений',
                            'Открытый конкурс с закрытой формой подачи предложений')
        if _type in offer_type:
            return 'offer'
        elif _type in auction_type:
            return 'auction'
        elif _type in competition_type:
            return 'competition'
        else:
            logger.error(f'{self.response.url} :: INVALID DATA TRADING TYPE')

    @property
    def get_string_organizer_div(self):
        """ :return div info """
        return self.response.xpath(GeneralInfoLocator.organizer_div_loc).get()

    def get_organizer(self):
        """ return organizer from tag <a>.text"""
        _div = self.get_string_organizer_div
        try:
            organizer = BS(str(_div), features='lxml').find('a').get_text()
            return dedent_func(organizer)
        except:
            logger.error(f'{self.response.url} :: ERROR WHILE GETTING ORGANIZER NAME')

    def get_organizer_contacts(self) -> dict:
        """ :return trading_org  """
        _div = self.get_string_organizer_div
        contacts = {'email': '', 'phone': ''}
        email = ''
        phone = ''
        paragraf_tag = BS(_div, 'lxml').find_all('p')
        if _div:
            for i in paragraf_tag:
                if '@' in i.get_text():
                    email = dedent_func(i.get_text().strip())
                text = replaceMultiple(i.get_text(), pattern_replace1, '')
                no_space = re.sub(r'\s', '', text)
                match = re.search(r'\d{6,}', no_space)
                if match:
                    phone = ''.join([x for x in i.get_text() if x.isdigit() or x == '-' or x == '(' or x == ')'])
            contacts['email'] = email
            contacts['phone'] = phone
            return contacts
        else:
            logger.error(f'{self.response.url} :: ERROR WHILE GETTING ORGANIZER NAME', exc_info=True)
            return contacts

    def get_trading_form(self):
        """ :return trading form (5)"""
        _form = self.get_string_trading_type
        _open = ('Продажа посредством публичного предложения',
                 'Открытый аукцион с открытой формой подачи предложений',
                 'Открытый аукцион с закрытой формой подачи предложений',
                 'Открытый конкурс с открытой формой подачи предложений',
                 'Открытый конкурс с закрытой формой подачи предложений')
        if _form in _open:
            return 'open'
        else:
            logger.error(f'{self.response.url} :: INVALID DATA STATUS')

    def get_status(self):
        """ :return status of trade (16)"""
        try:
            active = ('Идет приём заявок', 'Идет прием заявок',)
            pending = ('Торги объявлены',)
            ended = ('Заявки рассмотрены', 'Идёт аукцион',
                     'Подведение итогов', 'Приём заявок завершен', 'Рассмотрение заявок', 'Торги аннулированы',
                     'Торги не состоялись',
                     'Торги отменены',
                     'Торги приостановлены',
                     'Торги проведены')

            _status = self.response.xpath(GeneralInfoLocator.status_loc).get()
            if _status:
                status = dedent_func(_status.strip())
                if status and len(status) > 0:
                    if status in active:
                        return 'active'
                    elif status in pending:
                        return 'pending'
                    elif status in ended:
                        return 'ended'
                    else:
                        logger.critical(f'{self.response.url} :: INVALID STATUS')
                        return None
        except Exception as e:
            logger.critical(f'{self.response.url} :: INVALID DATA STATUS {e}', exc_info=True)
            return None

    def get_period_requests_auction(self):
        """ return list with statrt date request and end_date_requests """
        period_requests_auction = self.response.xpath(GeneralInfoLocator.date_request_period_auction).get()
        period_requests_auction = BS(str(period_requests_auction), features='lxml').get_text()
        period_requests_auction = dedent_func(period_requests_auction.strip())
        pattern = re.compile(r'\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}')
        periods = pattern.findall(period_requests_auction)
        # check if second time bigger
        check_if_second_eq_2 = what_time_bigger(periods[0], periods[1], self.response.url)
        if check_if_second_eq_2 == 2:
            return periods
        else:
            logger.error(
                f'{self.response.url} :: INVALID DATA GETTING LIST PERIODS START DATE REQUESTS AUCTION/COMPETITION')
            return None

    def start_date_req_auc(self):
        """ :return date of start date request """
        if self.get_period_requests_auction():
            return format_time(self.get_period_requests_auction()[0])
        else:
            logger.error(f'{self.response.url} :: INVALID START DATE REQUEST AUCTION')
            return None

    def end_date_request_auc(self):
        """ :return end of start date request """
        if self.get_period_requests_auction():
            return format_time(self.get_period_requests_auction()[1])
        else:
            logger.error(f'{self.response.url} :: INVALID END DATE REQUEST AUCTION')
            return None

    def start_date_trading_auc(self):
        """ :return start date trading auction """
        _div = self.response.xpath(GeneralInfoLocator.start_date_trading_auc_loc).get()
        if _div:
            _date = BS(str(_div), features='lxml').get_text()
            _date = dedent_func(_date.strip())
            pattern = re.compile(r'\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}')
            _date = pattern.findall(_date)
            if len(_date) == 1:
                return format_time(_date[0])

    def end_date_trading_auc(self):
        """ :return start date trading auction """
        _div = self.response.xpath(GeneralInfoLocator.end_date_trading_auc_loc).get()
        if _div:
            _date = BS(str(_div), features='lxml').get_text()
            _date = dedent_func(_date.strip())
            pattern = re.compile(r'\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}')
            _date = pattern.findall(_date)
            if len(_date) == 1:
                return format_time(_date[0])

    def get_documents_table(self):
        """ get documents(post data) """
        try:
            # list with form data (nimber of doc) andd doc's name
            lst_data = list()
            doc_table = self.soup.find('table', id='formMain:auctionDocs')
            if doc_table:
                for tr in doc_table.find_all('tr'):
                    _a = tr.find('a', id=re.compile(r'formMain:auctionDocs:\d+:typeDocName')).get('id')
                    _text = (
                        tr.find('td').find('span', class_='form-docum-note').get_text()
                        .replace('(', '').replace(',', '').strip()
                    )
                    lst_data.append((_a, _text))
                return lst_data
            else:
                logger.info(f'#############TAB WITH DOCS #######CHECK - SOMETHING WENT WRONG######{self.response.url}')
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR GETTING DOCUMENTS {e}')
            return list()

    def find_correct_form_number_1(self):
        """ return form with corret number : formMain:j_idt93_collapsed  or formMain:j_idt82_collapsed """
        lst = ['formMain:j_idt93_collapsed', 'formMain:j_idt82_collapsed']
        divs = self.soup.find_all('input', id=re.compile('formMain:j_idt\d+_collapsed'))
        for div in divs:
            div = div.get('id')
            if div in lst:
                return div

    def return_post_data(self, view_state, a_id) -> dict:
        """ return dict post data """
        _post = post_data_download
        _post['formMain:inputServerTime'] = return_parse_date()
        _post['javax.faces.ViewState'] = view_state
        data_ = self.find_correct_form_number_1()
        _post[data_] = 'false'
        # that param(a_id) must be deleted after call functions
        _post[a_id] = a_id
        return _post

    def download_trade(self, url: str, trading_id: str, cookies: str, view: str):
        load = DownloadFiles()
        lst_general = list()
        files_dir = FilesDir(relative_path, absolute_path)
        for t in self.get_documents_table():
            form_data, name = t
            if len(name) > 75:
                name = name[:30] + '_' + name[-35::1]
            name_on_server = files_dir.name_file_on_server(trading_id=trading_id, original_name=name)
            if not any(ele in name_on_server for ele in lst_exeption):
                files_dir.create_dir()
                path_absolute = files_dir.return_absolute_path(name_on_server)
                path_relative = files_dir.return_relative_path(name_on_server)
                request_data = RequestData(
                    url=url, referer=self.response.url,
                    host=host, cookies=cookies, method='POST',
                    data=self.return_post_data(view_state=view, a_id=form_data),
                    verify=False
                )
                if pathlib.Path(name_on_server).suffix in lst_exet_archive:
                    archive_lst = load.request_to_download_general(
                        request_data=request_data,
                        absolute_path=path_absolute,
                        relative_path=path_relative,
                        trading_id=trading_id
                    )
                    lst_general.extend(archive_lst)
                elif pathlib.Path(name_on_server).suffix in lst_exet:
                    load.request_to_download_general(
                        request_data=request_data,
                        absolute_path=path_absolute,
                        relative_path=path_relative,
                        trading_id=trading_id,
                    )
                    lst_general.append(
                        {
                            'original_name': name, 
                            'link': files_dir.return_relative_path(name_on_server).as_posix(),
                            'link_etp': self.response.url
                        }
                    )
                else:
                    lst_general.append({'original_name': name, 'link': '', 'link_etp': self.response.url})
                del post_data_download[form_data]
        return lst_general
