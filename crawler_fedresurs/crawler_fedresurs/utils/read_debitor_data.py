import os
import json
import logging
from .config import DIR_PROJECT, DIR_DEBITR

logger = logging.getLogger(__name__)


class ReadDebitr:

    def __init__(self):
        pass

    @classmethod
    def get_lst_files(cls):
        """return list with file in directory task_artitr"""
        lst_files = list()
        try:
            os.chdir(DIR_DEBITR)
        except Exception as e:
            logger.error(f'DIRECTORY {DIR_DEBITR} DOES NOT EXISTS \n {e}')
            return None
        try:
            for file in os.listdir():
                if file:
                    if file not in lst_files:
                        lst_files.append(file)
            return lst_files
        except Exception as e:
            logger.error(f'ERROR When Read File From Directory task_debitr \n {e}')
            return None

    @classmethod
    def read_data_files(cls) -> dict:
        """read data from all file that exists in directory DIR_DEBITR
           iterate throw all files -> read json data -> deserialize to dict
        """
        try:
            data_debtor = list()
            dict_data = dict()
            for file in cls.get_lst_files():
                with open(file, 'r') as f:
                    dict_ = json.load(f)
                    for k, v in dict_.items():
                        if k == 'debtor':
                            for val in v:
                                if val not in data_debtor:
                                    data_debtor.append(val)

            dict_data['debtor'] = data_debtor
            # retutn to project dir after read files  json_task_data
            os.chdir(DIR_PROJECT)
            return dict_data
        except Exception as e:
            logger.error(f'FILE DEBITR NOT FOUND {e}')
            return dict()

    @classmethod
    def get_debitr_inn(cls):
        """return arbitr names for post data if exist"""
        try:
            lst_debitr_name = cls.read_data_files().setdefault('debtor', list())
            if len(lst_debitr_name) > 0:
                return lst_debitr_name
            else:
                return None
        except Exception as e:
            logger.error(f'ERROR DURING GET debitr values from dict \n{e}')
            return None