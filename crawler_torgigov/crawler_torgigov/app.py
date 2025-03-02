import logging
import pathlib

from .utils.config import path_absolute, path_relative
from general_utils import DownloadFiles, FilesDir, dedent_func, CheckIfCorrectContactInfo, return_parse_date
from general_utils.config import lst_exeption, lst_exet, lst_exet_archive
from general_utils.models import RequestData

logger = logging.getLogger(__name__)


class Combo:
    def __init__(self, data):
        self.data = data

    def get_lots(self):
        return self.data['lots']

    def download_general(self):
        files_dir = FilesDir(path_relative, path_absolute)
        load = DownloadFiles()
        lst_general = list()
        for file in self.data['attachments']:
            link = f'https://torgi.gov.ru/new/file-store/v1/{file["fileId"]}'
            name = file['fileName']
            if len(name) > 75:
                name = name[:30] + '_' + name[-35::1]
            name_on_server = files_dir.name_file_on_server(self.trading_id, name)
            absolute_path = files_dir.return_absolute_path(name_on_server)
            relative_path = files_dir.return_relative_path(name_on_server)
            if not any(ele in name for ele in lst_exeption):
                files_dir.create_dir()
                request_data = RequestData(url=link)
                if pathlib.Path(name).suffix in lst_exet:
                    load.request_to_download_general(
                        request_data=request_data, absolute_path=absolute_path,
                        relative_path=relative_path, trading_id=self.trading_id,
                    )
                    lst_general.append(
                        {
                            'original_name': name,
                            'link': relative_path.as_posix(),
                            'link_etp': link
                        }
                    )
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    archive_lst = load.request_to_download_general(
                        request_data=request_data, absolute_path=absolute_path,
                        relative_path=relative_path, trading_id=self.trading_id
                    )
                    lst_general.extend(archive_lst)
                else:
                    lst_general.append(
                        {'original_name': name, 'link': None, 'link_etp': link}
                    )
        return lst_general

    def download_lot(self, lot):
        files_dir = FilesDir(path_relative, path_absolute)
        load = DownloadFiles()
        lst_lot = list()
        for file in lot['attachments']:
            link = f'https://torgi.gov.ru/new/file-store/v1/{file["fileId"]}'
            name = file['fileName']
            if len(name) > 75:
                name = name[:30] + '_' + name[-35::1]
            name_on_server = files_dir.name_file_on_server(self.trading_id, name, self.get_lot_number(lot))
            absolute_path = files_dir.return_absolute_path(name_on_server)
            relative_path = files_dir.return_relative_path(name_on_server)
            if not any(ele in name for ele in lst_exeption):
                files_dir.create_dir()
                request_data = RequestData(url=link)
                if pathlib.Path(name).suffix in lst_exet:
                    load.request_to_download_general(
                        request_data=request_data, absolute_path=absolute_path,
                        relative_path=relative_path, trading_id=self.trading_id, lot_number=self.get_lot_number(lot)
                    )
                    lst_lot.append(
                        {
                            'original_name': name,
                            'link': relative_path.as_posix(),
                            'link_etp': link
                        }
                    )
                elif pathlib.Path(name).suffix in lst_exet_archive:
                    archive_lst = load.request_to_download_general(
                        request_data=request_data, absolute_path=absolute_path,
                        relative_path=relative_path, trading_id=self.trading_id, lot_number=self.get_lot_number(lot)
                    )
                    lst_lot.extend(archive_lst)
                else:
                    lst_lot.append(
                        {'original_name': name, 'link': None, 'link_etp': link}
                    )
        return lst_lot

    @property
    def trading_id(self):
        return self.data['id']

    @property
    def trading_link(self):
        return f'https://torgi.gov.ru/new/public/notices/view/{self.trading_id}'

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        type_value = self.data['biddForm']['name']
        d = {
            'auction': ['Электронный аукцион']
        }
        for key in d:
            if type_value in d[key]:
                return key
        logger.error(f'{self.trading_link} :: Unknown trading type')

    @property
    def trading_form(self):
        return 'open'

    @property
    def trading_org(self):
        return dedent_func(self.data['bidderOrg']['name'])

    # @property
    # def trading_org_inn(self):
    #     return CheckIfCorrectContactInfo.check_inn(self.data['bidderOrg']['inn'])

    @property
    def trading_org_contacts(self):
        return {
            'email': CheckIfCorrectContactInfo.check_email(self.data['bidderOrg']['email']),
            'phone': CheckIfCorrectContactInfo.check_phone(self.data['bidderOrg']['tel'])
        }

    # @property
    # def debtor_inn(self):
    #     ...

    def get_address(self, lot):
        return lot['estateAddress']

    @property
    def encumbrance(self):
        ...

    @property
    def description_encumbrance(self):
        ...

    # @property
    # def arbit_manager(self):
    #     return self.data['bidderOrg']['contPerson']

    @property
    def status(self):
        form_value = self.data['noticeStatus']
        d = {
            'active': ['APPLICATIONS_SUBMISSION']
        }
        for key in d:
            if form_value in d[key]:
                return key
        logger.error(f'{self.trading_link} :: Unknown trading form')

    def get_category(self, lot):
        return lot['category']['name']

    def get_lot_id(self, lot):
        return lot['id']

    def get_lot_link(self, lot):
        return f'https://torgi.gov.ru/new/public/lots/lot/{self.get_lot_id(lot)}/(lotInfo:info)?fromRec=false#lotInfoSection-info'

    def get_lot_number(self, lot):
        return lot['lotNumber']

    def get_short_name(self, lot):
        return lot['lotName']

    def get_lot_info(self, lot):
        return lot['lotDescription']

    def get_deposit(self, lot):
        return lot['deposit']

    @property
    def property_information(self):
        ...

    @property
    def start_date_requests(self):
        return return_parse_date(self.data['biddStartTime'])

    @property
    def end_date_requests(self):
        return return_parse_date(self.data['biddEndTime'])

    @property
    def start_date_trading(self):
        return return_parse_date(self.data['auctionStartDate'])

    @property
    def end_date_trading(self):
        date = None
        if self.trading_type == 'offer':
            date = self.data['auctionStartDate']
        elif self.trading_type == 'auction':
            for el in self.data['attributes']:
                if el['fullName'] == 'Дата, время подведения результатов торгов':
                    date = el.get('value')
        else:
            pass
        if date:
            return return_parse_date(date)

    def get_start_price(self, lot):
        return lot['priceMin']

    def get_step_price(self, lot):
        return lot['priceStep']

    @property
    def periods(self):
        ...
