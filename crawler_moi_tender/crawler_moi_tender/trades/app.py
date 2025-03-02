import pathlib
import re

from bs4 import BeautifulSoup, NavigableString

from general_utils import format_time
from general_utils.config import lst_exeption, lst_exet, lst_exet_archive
from general_utils.location import RegionIdentifier
from ..utils.check_inn_email_phone import CheckIfCorrectContactInfo
from ..utils.config import data_origin_url
from ..utils.download import DownloadFiles
from ..utils.work_with_path_and_dir import GeneralFilesDir
from ..utils.work_with_text_and_number import dedent_func, contains, make_float
from ..utils.working_with_url import UrlConfig


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, 'lxml')
        self.check = CheckIfCorrectContactInfo()
        self.general = GeneralFilesDir()
        self.url = UrlConfig()

    def get_lots(self):
        # tenders = self.soup.find('div', class_='tenders')
        # if not tenders:
        #     return []
        lots = self.soup.find_all('div', class_='tender')
        lots_data = []
        for lot in lots:
            status = dedent_func(lot.find('div', class_='status').get_text(strip=True))
            if 'закрыт' in status.lower():  # Доступ по паролю
                trading_form = 'closed'
                status = 'ended'
            else:
                trading_form = 'open'
                status = 'active'
            short_desc = lot.find('div', class_='short-desc')
            trading_link = short_desc.find('a')['href']
            short_name = dedent_func(short_desc.find('a').get_text(strip=True))

            region_city = lot.find('div', class_='region-city')
            span = region_city.find('span')
            address = dedent_func(span.find('b').get_text())
            region = RegionIdentifier.get_region(address)

            trading_id = trading_number = dedent_func(
                lot.find('div', class_='num').get_text(strip=True).replace('№', '')
            )
            start_price = lot.find('div', class_='price')
            if start_price:
                start_price = start_price.findNext('div').get_text().strip()
                if start_price:
                    return make_float(start_price)
            category = dedent_func(lot.find('div', class_='tender-cat').find('b').get_text(strip=True))

            company = lot.find('div', class_='company').find('a')
            org = dedent_func(company.get_text(strip=True))
            org_link = dedent_func(company['href'])

            lots_data.append(
                {
                    'trading_id': trading_id, 'trading_link': trading_link, 'trading_number': trading_number,
                    'trading_form': trading_form, 'start_price': start_price,
                    'category': category, 'org': org, 'org_link': org_link, 'status': status, 'short_name': short_name,
                    'address': address, 'region': region
                }
            )
        return lots_data

    def download_trade(self, trading_id):
        dir = self.general
        download = DownloadFiles()
        general_lst = list()
        links = self.soup.find('div', class_='title', text=contains('Документация'))
        if links:
            links = links.parent.find_all('div', class_='isfile')
        for link in links or []:
            a = link.find('a')
            name = a.get_text().strip()
            link = self.url.url_join(data_origin_url, a.get("href"))
            if not any(ele in name for ele in lst_exeption):
                if pathlib.Path(name).suffix in lst_exet:
                    dir.create_dir()
                    if len(name) > 75:
                        file_name_server = name[0][:30] + "_" + name[0][-35::1]
                    else:
                        file_name_server = name[0]
                    name_on_server = dir.name_file_on_server(trading_id, file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    download.request_to_download_general(url=link, referer=self.response.url, _abs_path=_path_absolute)
                    _path_relative = dir.name_in_column_files(name_on_server, )
                    general_lst.append(
                        {"original_name": name, "link": _path_relative, "link_etp": link}
                    )
                    # FILES INSIDE ARCHIVE
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    if len(name) > 75:
                        file_name_server = name[:30] + "_" + name[-35::1]
                    else:
                        file_name_server = name
                    name_on_server = dir.name_file_on_server(trading_id, file_name_server)
                    _path_absolute = dir.return_absolute_path(name_on_server)
                    dir.create_dir()
                    lst_files = download.request_to_download_general(
                        url=link,
                        referer=self.response.url,
                        _abs_path=_path_absolute,
                        _id=trading_id,
                        _relative_path=dir.return_download_dir_etp(),
                    )
                    general_lst.extend(lst_files)
                else:
                    general_lst.append({"original_name": name, "link": "", "link_etp": link})
        return general_lst

    def download_lot(self):
        return []

    @property
    def trading_org_contacts(self):
        phone = None
        profile_page = self.get_profile_page()
        email = profile_page.find('a', href=re.compile('mailto:'))
        if email:
            email_ = self.check.check_email(dedent_func(email.get('href').removeprefix('mailto:')))
            phone = email.find_next('div', class_='value')
            if phone:
                phone = self.check.check_phone(phone.get_text())
            email = email_
        return {"email": email, "phone": phone}

    @property
    def trading_org_inn(self):
        profile_page = self.get_profile_page()
        inn = profile_page.find('div', class_='value', text=contains('ИНН'))
        if inn:
            inn = inn.get_text(strip=True).split()[-1]
            return dedent_func(self.check.check_inn(inn))

    def get_profile_page(self):
        return self.soup.find('div', class_='profile-page')

    @property
    def encumbrance(self):
        ...

    @property
    def description_encumbrance(self):
        ...

    @property
    def lot_number(self):
        ...

    @property
    def lot_info(self):
        info = self.soup.find('div', class_='description')
        if info:
            return dedent_func(info.get_text())

    @property
    def property_information(self):
        ...

    @property
    def start_date_requests(self):
        start = self.soup.find('div', class_='label', text=contains('Дата публикации извещения')).find_next(
            'div').get_text(strip=True)
        return format_time(start)

    @property
    def end_date_requests(self):
        div = self.soup.find('div', class_='label', text=contains('Дата окончания приема заявок')).find_next('div')
        return format_time(''.join(
            child for child in div.contents if isinstance(child, NavigableString)
        ).strip().replace('/ ', ''))

    @property
    def start_date_trading(self):
        ...

    @property
    def end_date_trading(self):
        ...

    @property
    def index(self):
        ...

    @property
    def min_price(self):
        ...

    @property
    def deposit(self):
        ...

    @property
    def step_price(self):
        ...

    @property
    def periods(self):
        ...

    @property
    def quantity(self):
        ...

    @property
    def unit(self):
        ...
