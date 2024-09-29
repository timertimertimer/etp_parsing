from icecream import ic

from ..locators.pre_trade_page_locator import SearchLocator
from bs4 import BeautifulSoup as BS
import logging
from ..utils.config import data_origin_url
from ..utils.work_with_text_and_number import dedent_func
from ..utils.working_with_time import format_time_period
from ..utils.working_with_url import UrlConfig
import re
import math

logger = logging.getLogger(__name__)


class PreTradePage:

    def __init__(self, _response):
        self.response = _response
        self.loc = SearchLocator
        self.url = UrlConfig()
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')

    @property
    def get_link_to_serp_trade(self):
        """ get link for follow to serp page with lots links """
        try:
            section_with_link = self.response.xpath(self.loc.link_to_serp_trades_loc).get()
            if section_with_link:
                link = BS(str(section_with_link), features='lxml').find('a')
                if link:
                    # from link delete dot that is on the begining
                    link = re.sub(r'^.', '', link.get('href'))
                    # from data origin delete '/' from the end
                    return self.url.url_join(data_origin_url[:-1], link)
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR GETTING LINK TO TRADING LOTS OF AKOSTA\n{e}')
            with open('main_link_to_trades_ERROR.txt', 'w') as f:
                f.write(self.response.text)
                return None

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

    @property
    def get_total_and_current_page(self) -> tuple or None:
        """:return total page return tuple"""
        try:
            span = self.soup.find('span', class_='ui-paginator-current').get_text()
            print('THIS IS SPAN "PRE_TRADE"', span)
            pattern = re.compile(r'\d+\/\d+')
            p = pattern.findall(span)
            current_page = ''.join(p).split('/')[0]
            total_page = ''.join(p).split('/')[1]
            return int(current_page), int(total_page)
        except Exception as e:
            logger.error(
                f'{self.response.url} ::{e}::\n page download with error -> error file name "pagination_error.txt" ')
            with open('pagination_error.txt', 'w') as f:
                f.write(self.response.text)
            return None

    def get_trade_links(self):
        """ :return list with links info to trading page """
        try:
            links = self.soup.find('div', id='formMain:lotListTable')
            lst_links = links.find_all('tr', attrs={'data-ri': re.compile(r'\d+')})
            if lst_links and len(lst_links) > 0:
                return lst_links
            else:
                logger.error(f'{self.response.url} :: DURING GETTING LINKS TO TRADE PAGES OCCURE ERROR')
                with open('getting_links_to_trading_page_1.txt', 'w') as f:
                    f.write(self.response.text)
        except Exception as e:
            logger.error(f'{self.response.url} ::{e}:: DURING GETTING LINKS TO TRADE PAGES OCCURE ERROR(1)',
                         exc_info=True)
            with open('getting_links_to_trading_page.txt', 'w') as f:
                f.write(self.response.text)

    def get_id_a_trade(self):
        """ get tag <tr>. From tr get <a> fetch value of id for put to form data """
        try:
            lst_with_id = list()
            for tr in self.get_trade_links():
                soup_ = BS(str(tr), features='lxml')
                _id = soup_.find('a').get('id')
                if _id:
                    lst_with_id.append(_id)
            return lst_with_id
            logger.error(f'{self.response.url} :: EMPTY  DATA LINK TO TRADE')
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: ERROR GETTING FORM DATA LIKE A LINK')
            with open('error_form_data_link.txt', 'w') as f:
                f.write(self.response.text)

    def get_id_a_trade_1(self, tr):
        """ get tag <tr>. From tr get <a> fetch value of id for put to form data """
        try:
            lst_with_id = list()
            soup_ = BS(str(tr), features='lxml')
            _id = soup_.find('a').get('id')
            if _id:
                lst_with_id.append(_id)
            return lst_with_id
            logger.error(f'{self.response.url} :: EMPTY  DATA LINK TO TRADE')
        except Exception as e:
            logger.error(f'{self.response.url} :{e}: ERROR GETTING FORM DATA LIKE A LINK')
            with open('error_form_data_link.txt', 'w') as f:
                f.write(self.response.text)

    def get_only_one_needed_id(self, trade):
        """
            :arg trade
        """
        try:
            all_id = self.get_id_a_trade()
            lst_temp = list()
            lst_id_number = list()
            finall_set = set()
            for i in all_id:
                number = self.soup.find('a', id=i)
                if number:
                    number = dedent_func(number.get_text().strip())
                    if trade in number:
                        lst_temp.append(number)
                        lst_id_number.append((number, i))
            set_trading_number = set(lst_temp)
            if 0 <= len(set_trading_number) <= 1:
                _id = ''.join(lst_id_number[0][1])
                return [(_id, trade)]
            else:
                num = list()
                _id = list()
                for i in list(lst_id_number):
                    date = self.check_start_date_requet(i[0])
                    if len(date) > 0:
                        if date[0] > '2019-12-31 23:59:59':
                            if i[0] not in num:
                                num.append(i[0])
                                _id.append(i[1])
                total = list(zip(_id, num))
            return total
        except Exception as e:
            logger.error(f'{e}', exc_info=True)

    def check_start_date_requet(self, text):
        """ check if start date request bigger than 2020-01-01 00:00:00 """
        out_put_list = list()
        dates = self.response.xpath(self.loc.start_date_request.format(text)).getall()
        for d in dates:
            out_put_list.append(format_time_period(d))
        return out_put_list

    # !!!!!!!!!!
    def get_trading_number(self, page_number):
        """ fetch trading id for search request another spider """
        try:
            _id = self.get_id_a_trade()
            trading = self.response.xpath(self.loc.trading_number_loc.format(_id)).get()
            tra = BS(str(trading), features='lxml').get_text()
            return dedent_func(tra.strip())
        except Exception as ex:
            logger.critical(f'ON PAGE - {page_number} :: ERROR GETTING TRADING ID {ex}')

    # !!!!!!!!!!
    def get_trading_number_1(self, _id, page_number):
        """ fetch trading id for search request another spider """
        try:
            # _id = self.get_id_a_trade_1(tr)
            trading = self.response.xpath(self.loc.trading_number_loc.format(_id[0])).get()
            tra = BS(str(trading), features='lxml').get_text()
            return dedent_func(tra.strip())
        except Exception as ex:
            logger.critical(f'ON PAGE - {page_number} :: ERROR GETTING TRADING ID {ex}')

    def get_view_after_first_page(self, html):
        """ if current page queal or higher then 2  """
        try:
            string = str(html).replace('&lt;', '<').replace('&gt;', '>')
            pattern = re.compile('<update id="j_id1:javax.faces.ViewState:0"><!\[CDATA\[(.*)\]\]></update>')
            res = pattern.findall(string)[0]
            if res:
                if len(res) > 0:
                    res = str(res).replace(']]><![CDATA[le', '')
                    return res
        except:
            logger.error(f'{self.response.url} :: INVALID DATA VIEWSTATE (when page >= 2', exc_info=True)

    def get_trade_links_2(self, page_number, total_pages):
        """ post data for trading pages on page 2 (pagination) or highter different then on page one """
        try:
            temporary_list = list()
            lst = list()
            lst_exc = ['<', '>', '!', '[', ']', 'C', 'D', 'A', 'T', 'A', '\'']
            trading_text = re.findall(r'\d{3,5}-\D{4}', str(self.response.text))
            if len(trading_text) < 50:
                print('NOT ALL ', page_number)
                clean_lst = list()
                extra_search = re.findall(r'\d{1,4}\]\]><\!\[CDATA\[\d{1,3}-\D{4}', ''.join(self.response.text))
                for i in extra_search:
                    number = ''.join(filter(lambda x: x not in lst_exc, i))
                    clean_lst.append(('trading_number', number))
                # with open(f'{page_number}_text.txt', 'w') as f:
                #     f.write(self.response.text)
                temporary_list.extend(clean_lst)
            for t in trading_text:
                t = ''.join(filter(lambda x: x not in lst_exc, t))
                temporary_list.append(('trading_number', t))
            return temporary_list
        except Exception as ex:
            with open(f'{page_number}_error_page_none.txt', 'w') as f:
                f.write(self.response.text)
            logger.error(f' ERROR page number - {page_number}, {ex}')

    # def get_trade_links_2(self, page_number):
    #     """ post data for trading pages on page 2 (pagination) or highter different then on page one """
    #     try:
    #         temporary_list = list()
    #         lst = list()
    #         trading_text = re.findall(r'\d{4}-\D{4}', self.response.text)
    #         for a in self.soup.find_all('a'):
    #             _id = a.get('id')
    #             if _id:
    #                 _id = re.sub(r'\]\]\>\<\!\[CDATA\[', '', str(_id)).strip()
    #             if 'OpenCard' not in _id:
    #                 # trading_text = self.soup.find('a', id=_id)
    #                 temporary_list.append(_id)
    #         # print(len(temporary_list), 'tem')
    #         # print(len(trading_text), 'text')
    #         for n, _id in enumerate(temporary_list):
    #             try:
    #                 text = dedent_func(trading_text[n].strip())
    #             except IndexError as ex:
    #                 text = None
    #                 with open(f'{page_number}_error_page_none.txt', 'w') as f:
    #                     f.write(self.response.text)
    #                 logger.error(f' ERROR page number - {page_number}, {ex}')
    #             lst.append((_id, text))
    #         return lst
    #     except:
    #         logger.error(f'{self.response.url} ::: ERROR GETTITNG POST DATA WHEN PAGE > 2', exc_info=True)

    def count_total_pages(self, html):
        """ count total pages from getting number of total lots
            :arg html -> html of page
        """
        try:
            string = str(html).replace('&lt;', '<').replace('&gt;', '>')
            pattern = re.compile('type="args">{"totalRecords":(.*)}</extension>')
            res = ''.join([x for x in pattern.findall(string)[0] if x.isdigit()])
            try:
                res = int(res)
                number_of_pages = math.ceil(int(res) / 50)
                return number_of_pages
            except:
                res = None
                logger.error(f'{self.response.url} :: total pages not int')
                return res
        except:
            logger.error(f'{self.response.url} :: INVALID DATA VIEWSTATE (when page >= 2', exc_info=True)
