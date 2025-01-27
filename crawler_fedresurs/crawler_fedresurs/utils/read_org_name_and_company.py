import os
import json
import logging
from .config import DIR_PROJECT, DIR_ORGANIZER, pattern_name_cut, pattern_company_cut

logger = logging.getLogger(__name__)


class ReadOrgName:

    def __init__(self):
        pass

    @classmethod
    def get_lst_files(cls):
        """return list with file in directory task_organizer"""
        lst_files = list()
        try:
            os.chdir(DIR_ORGANIZER)
        except Exception as e:
            logger.error(f'DIRECTORY {DIR_ORGANIZER} DOES NOT EXISTS \n {e}')
            return None
        try:
            for file in os.listdir():
                if file:
                    if file not in lst_files:
                        lst_files.append(file)
            return lst_files
        except Exception as e:
            logger.error(f'ERROR When Read File From Directory tasl_organizer \n {e}')
            return None

    @classmethod
    def get_org_name_data(cls):
        """retun organizers name for post data if exist"""
        try:
            lst_ogr_name = cls.read_data_files().setdefault('organizer', list())
            clean_org_name = list()
            if len(lst_ogr_name) > 0:
                company_list = cls.get_org_company_data()
                for n in lst_ogr_name:
                    if n not in clean_org_name and n not in company_list:
                        clean_org_name.append(n)
                return clean_org_name
            else:
                return list()
        except Exception as e:
            logger.error(f'ERROR DURING GET lst_ogr_name values from dict \n{e}')
            return list()

    @classmethod
    def get_org_company_data(cls):
        """return organizers company for post data if exist"""
        try:
            lst_ogr_company = cls.read_data_files().setdefault('organizer', list())
            clean_org_company = list()
            if len(lst_ogr_company) > 0:
                for i in pattern_company_cut:
                    for y in lst_ogr_company:
                        if i in ''.join(y).lower() or '"' in ''.join(y).lower():
                            if y not in clean_org_company:
                                clean_org_company.append(y)

                return clean_org_company
            else:
                return list()
        except Exception as e:
            logger.error(f'ERROR DURING GET organizer_company values from dict \n{e}')
            return None

    @classmethod
    def read_data_files(cls) -> dict:
        """read data from all file that exists in directory DIR_ORGANIZER
           iterate throw all files -> read json data -> deserialize to dict -> iterate throw dict ->
           -> sort values according key and append to list -> retun dict: keys org name or company and values list
           with query data according keys
        """
        try:
            data_org_name = list()
            #data_org_company = list()
            dict_data = dict()
            for file in cls.get_lst_files():
                with open(file, 'r') as f:
                    dict_ = json.load(f)
                    for k, v in dict_.items():
                        if k == 'organizer':
                            for val in v:
                                if val not in data_org_name:
                                    data_org_name.append(val)
                        # elif k == 'organizer_name':
                        #     for val in v:
                        #         # val = ''.join(val).lower().replace('\'', '').replace('«', '').replace('»', '').replace(
                        #         #     '"', '').title().strip()
                        #         if val not in data_org_name:
                        #             data_org_name.append(val)

            dict_data['organizer'] = data_org_name
            # dict_data['organizer_name'] = data_org_name
            # retutn to project dir after read files fro, json_task_data
            os.chdir(DIR_PROJECT)
            return dict_data
        except Exception as e:
            logger.error(f'FILE ORGANIZER NOT FOUND {e}')
            return dict()
