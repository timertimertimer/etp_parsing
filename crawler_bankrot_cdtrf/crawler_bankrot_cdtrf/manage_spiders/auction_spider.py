from general_utils.config import lst_exet_archive, lst_exeption
from ..utils.config import trade_page_file, relative_path
from ..locators_and_attributes.locators_attributes import Auction
from ..utils.working_with_time import format_time_auction

from ..utils.download import *

MAIN_LST = [
    'https://bankrot.cdtrf.ru/public/undef/card/pdoc.aspx?tradeid=60635&id=f13f29f6-71b7-4fd2-81ca-94dd9c9631c9',
    'https://bankrot.cdtrf.ru/public/undef/card/pdoc.aspx?tradeid=60635&id=502ddd72-20e6-40a0-8850-7737c8e9e5b5',
    'https://bankrot.cdtrf.ru/public/undef/card/pdoc.aspx?tradeid=60635&id=40670a5d-c8d6-4a24-988d-a909640c02f4',
    # 'https://httpbin.org/ip', 'https://httpbin.org/ip', 'https://httpbin.org/ip',
    # 'https://httpbin.org/user-agent',
    # 'https://httpbin.org/user-agent',
    # 'https://httpbin.org/user-agent'

]
logger = logging.getLogger(__name__)


class AuctionSpider:

    def __init__(self, response_):
        self.response = response_
        self.soup = BS(str(self.response.body.decode('utf-8')).replace('&lt;', '<').replace('&gt;', '>'),
                       features='lxml')
        self.loc = Auction
        self.url = UrlConfig()

    @property
    def get_trading_type(self):
        """ return trading type """
        trading_type = self.response.xpath(self.loc.trading_type_loc).get()
        if trading_type and len(trading_type) > 0:
            type_ = dedent_func(BS(str(trading_type), features='lxml').get_text()).strip()
            if type_ in ['Аукцион', 'Открытый аукцион', 'Закрытый аукцион']:
                return 'auction'
            else:
                logger.error(f'{self.response.url} :: INVALID DATA TRADING TYPE')
                return 'auction'

    @property
    def start_date_req(self):
        """:return start date request for auction"""
        try:
            s = self.soup.find(id=self.loc.start_date_req_loc)
            if s:
                date = dedent_func(s.get_text())
                return format_time_auction(date)
        except:
            logger.error(f'{self.response.url} :: INVAID DATA START DATE REQUST AUCTION')

    @property
    def end_date_req(self):
        """:return end date request for auction"""
        try:
            e = self.soup.find(id=self.loc.end_date_req_loc)
            if e:
                date = dedent_func(e.get_text())
                return format_time_auction(date)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE TRADING')

    @property
    def start_date_trading(self):
        """:return start date trading date"""
        try:
            st = self.soup.find(id=self.loc.start_date_trading)
            if st:
                date = dedent_func(st.get_text())
                return format_time_auction(date)
            else:
                st = self.soup.find(id=self.loc.extra_start_date_trading)
                if st:
                    date = dedent_func(st.get_text())
                    return format_time_auction(date)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA START DATE TRADING')

    @property
    def end_date_trading(self):
        """:return start date trading date"""
        try:
            st = self.soup.find(id=self.loc.end_date_trading)
            if st:
                date = dedent_func(st.get_text())
                return format_time_auction(date)
        except:
            logger.error(f'{self.response.url} :: INVALID DATA END DATE TRADING')

    @property
    def start_price(self):
        """return start price"""
        try:
            p = self.soup.find(id=self.loc.start_price_auc_loc)
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID DATA START PRICE\n{e}')

    @property
    def step_price(self):
        """return start price"""
        try:
            p = self.soup.find(id=self.loc.step_price_auc_loc)
            if p:
                p = re.sub(r'\s', '', dedent_func(p.get_text().strip()).replace(',', '.'))
                p = ''.join([x for x in p if x.isdigit() or x == '.'])
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f'{self.response.url} :: INVALID DATA STEP PRICE\n{e}')

    # FILES
    @property
    def list_link_to_file_lot(self):
        """:return list with tags <a> -> that contains link to page with file"""
        try:
            links = self.response.xpath(self.loc.to_lot_files_loc).getall()
            if len(links) > 0:
                return links
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA LINK TO LOT FILE\n{e}')
            return None

    @property
    def clean_files_lot_links(self):
        """itterate througth list with tag <a> and get href to file page"""
        if self.list_link_to_file_lot:
            clean_set = set()
            for link in self.list_link_to_file_lot:
                try:
                    link = BS(str(link), features='lxml').find('a').get('href')
                    link = self.url.parse_url(self.url.url_join(trade_page_file, link))
                    clean_set.add(link)
                finally:
                    continue
            return clean_set

    async def files_lot(self, file_id, referer):
        lst = self.clean_files_lot_links
        f = asyncio.run(main(lst, file_id, referer))
        return f

    def general_file_link_doc_1(self):
        """get first doc link for general"""
        try:
            td = self.response.xpath(self.loc.to_dohovor_loc).get()
            if td:
                link = BS(str(td), features='lxml').find('a')
                if link:
                    return self.url.parse_url(self.url.url_join(trade_page_file, link.get('href')))
                else:
                    return list()
        except:
            logger.error(f'{self.response.url} :: ERROR GETTING GREF TO FILE GENERAL')

    def general_file_link_doc_2(self):
        """get second doc link for general"""
        try:
            td = self.response.xpath(self.loc.to_proekt_loc).get()
            if td:
                link = BS(str(td), features='lxml').find('a')
                if link:
                    return self.url.parse_url(self.url.url_join(trade_page_file, link.get('href')))
                else:
                    return list()
        except Exception as e:
            logger.error(f'{self.response.url} :: ERROR GETTING GREF TO FILE GENERAL\n{e}')

    def find_all_files(self, referer):
        """ find all files on the page """
        link = self.soup.find_all('a', {'href': re.compile(r'undef/card/download.aspx\?fileid.+0')})
        if link:
            return link
        else:
            logger.error(f'{referer} :: ERROR WITH DOCUMENTS', exc_info=True)
            with open('ERROR_doc_page.txt', 'w') as f:
                f.write(self.response.text)
            return list()

    def return_general(self, lst: list) -> list:
        """return all general file info"""
        try:
            general = list()
            for f in lst:
                file_ = BS(str(f), features='lxml')
                if file_:
                    file_ = file_.find('a')
                    if file_:
                        file_link = re.sub(r'\s', '', dedent_func(file_.get('href')))
                        file_name = file_.get_text()
                        general.append({'original_name': dedent_func(file_name),
                                        'link': '',
                                        'link_etp': self.url.url_join(data_origin_url, file_link)})
            return general
        except:
            logger.error(f'{self.response.url} :: INVALID DATA FILES GENERAL')
            return list()

    def return_and_download_lot_files(self, file_id, referer, lst, _id, lot_num, _relative_path=relative_path):
        """return and download all  lot file """
        from ..utils.download2 import DownloadFiles, GeneralFilesDir
        _dir = GeneralFilesDir()
        _down = DownloadFiles()
        try:
            lot = list()
            for f in lst:
                file_ = BS(str(f), features='lxml')
                if file_:
                    file_ = file_.find('a')
                    if file_:
                        file_link = re.sub(r'\s', '', dedent_func(file_.get('href')))
                        link_etp = self.url.url_join(data_origin_url, file_link)
                        # name on etp
                        file_name = file_.get_text()
                        if not any(ele in file_name for ele in lst_exeption):
                            path_on_server = ''
                            if pathlib.Path(file_name.replace(' ', '')).suffix in lst_exet:
                                if len(file_name) > 72:
                                    file_name = file_name[-45::1]
                                name_on_server = _dir.name_file_on_server(file_id, file_name)
                                _dir.create_dir()
                                path_on_server = _dir.name_in_column_files(name_on_server)
                                _down.request_to_download_general(url=link_etp, referer=referer,
                                                                  original_name=name_on_server)
                                lot.append({'original_name': dedent_func(file_name),
                                            'link': path_on_server,
                                            'link_etp': link_etp})
                            elif pathlib.Path(file_name.replace(' ', '')).suffix in lst_exet_archive:
                                if len(file_name) > 72:
                                    file_name = file_name[-45::1]
                                name_on_server = _dir.name_file_on_server(file_id, file_name)
                                _dir.create_dir()
                                path_on_server = _dir.name_in_column_files(name_on_server)
                                arch_fiels = _down.request_to_download_general(url=link_etp, referer=referer,
                                                                               original_name=name_on_server, _id=_id,
                                                                               lot_num=lot_num, _relative_path=relative_path)
                                lot.extend(arch_fiels)
            return lot
        except Exception as e:
            logger.error(f'{self.response.url} :: INVALID DATA FILES LOT\n{e}', exc_info=True)
            return list()
