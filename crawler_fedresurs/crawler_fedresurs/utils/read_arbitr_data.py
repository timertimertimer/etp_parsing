import os
import json
import logging
from .config import DIR_PROJECT, DIR_ARBITOR

logger = logging.getLogger(__name__)


class ReadArbitr:

    def __init__(self):
        pass

    @classmethod
    def get_lst_files(cls):
        """return list with file in directory task_artitr"""
        lst_files = list()
        try:
            os.chdir(DIR_ARBITOR)
        except Exception as e:
            logger.error(f'DIRECTORY {DIR_ARBITOR} DOES NOT EXISTS \n {e}')
            return None
        try:
            for file in os.listdir():
                if file:
                    if file not in lst_files:
                        lst_files.append(file)
            return lst_files
        except Exception as e:
            logger.error(f'ERROR When Read File From Directory task_arbitr \n {e}')
            return None

    @classmethod
    def read_data_files(cls) -> dict:
        """read data from all file that exists in directory DIR_ARBITR
           iterate throw all files -> read json data -> deserialize to dict
        """
        try:
            data_arbitr = list()
            dict_data = dict()
            for file in cls.get_lst_files():
                with open(file, 'r') as f:
                    dict_ = json.load(f)
                    for k, v in dict_.items():
                        if k == 'arbitrator':
                            for val in v:
                                if val not in data_arbitr:
                                    data_arbitr.append(val)

            dict_data['arbitrator'] = data_arbitr
            # retutn to project dir after read files  json_task_data
            os.chdir(DIR_PROJECT)
            return dict_data
        except Exception as e:
            logger.error(f'FILE ARBITR NOT FOUND {e}')
            return dict()

    @classmethod
    def get_arbitr_names(cls):
        """return arbitr names for post data if exist"""
        try:
            lst_arbitr_name = cls.read_data_files().setdefault('arbitrator', list())
            if len(lst_arbitr_name) > 0:
                return lst_arbitr_name
            else:
                return None
        except Exception as e:
            logger.error(f'ERROR DURING GET arbitr_name values from dict \n{e}')
            return None