#!/usr/bin/python3
import asyncio
import logging
import pickle
import socket
from configparser import ConfigParser
from itertools import chain
from pathlib import Path

import mysql.connector
import websockets

logging.basicConfig(filename='service_get_data_for_fedres.log', level=logging.ERROR)

# data for manage connection and sending file
HEADER = 64
FORMAT = 'utf-8'
SERVER = 'localhost'
PORT = 55555


__path_config_ini = f'/home/parser/etp_parsing'
__config_ini = 'config.ini'
mysql_configure_file = Path(__path_config_ini, __config_ini)


# data for collaborate with database
def read_db_config(filename=mysql_configure_file, section='mysql'):
    parser = ConfigParser()
    parser.read(filename)
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))
    return db
connect_db = read_db_config()

TABLE = 'fedres_data'
DATABASE = 'main_parsing'

host = connect_db['host']
user = connect_db['user']
passwd = connect_db['password']


class GetDatabaseData:

    def __init__(self) -> None:
        self.create_connection()

    def create_connection(self):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=DATABASE,

        )
        self.mycursor = self.mydb.cursor()

    def get_arbitr(self):
        self.mycursor.execute(
            f"""SELECT type, search_string FROM {TABLE} where type='arbitrator' and status='active' ORDER BY search_string LIMIT 40 """)
        records = self.mycursor.fetchall()
        return records

    def get_debitor(self):
        self.mycursor.execute(f"""SELECT type, search_string FROM {TABLE} where type='debtor' and status='active' ORDER BY search_string LIMIT 40 """)
        records = self.mycursor.fetchall()
        return records

    def get_org_name(self):
        self.mycursor.execute(
            f"""SELECT type, search_string FROM {TABLE} where type='organizer' and status='active' ORDER BY search_string LIMIT 40 """)
        records = self.mycursor.fetchall()
        return records

    # def get_org_company(self):
    #     self.mycursor.execute(
    #         f"""SELECT type, search_string FROM {TABLE} where type='organizer_company' and status='active' """)
    #     records = self.mycursor.fetchall()
    #     return records

    def close_conn(self):
        self.mycursor.close()
        self.mydb.close()


class FormatDbDataToDict(GetDatabaseData):

    def __init__(self) -> None:
        super().__init__()

    def dict_arbitr(self) -> dict:
        """return dict with key: arbitr and value: list with names"""
        arbitr = dict()
        arb_lst = list()
        if self.get_arbitr():
            for a in self.get_arbitr():
                arb_lst.append(a[1])
        arbitr['arbitrator'] = arb_lst
        return arbitr

    def dict_org_name(self):
        """return dict with key:organizer names and value: list with names"""
        org_names = dict()
        org_name_lst = list()
        if self.get_org_name():
            for org_name in self.get_org_name():
                org_name_lst.append(org_name[1])
        org_names['organizer'] = org_name_lst
        return org_names

    # def dict_org_company(self):
    #     """return dict with key:organizer company and value: list with companies"""
    #     org_companies = dict()
    #     org_company_lst = list()
    #     if self.get_org_company():
    #         for org_company in self.get_org_company():
    #             org_company_lst.append(org_company[1])
    #     org_companies['organizer_company'] = org_company_lst
    #     return org_companies

    def dict_debitor(self):
        """return dict with key: debitor and value: list with debitors inn"""
        debitor = dict()
        debitor_lst = list()
        if self.get_debitor():
            for deb in self.get_debitor():
                debitor_lst.append(deb[1])
        debitor['debtor'] = debitor_lst
        return debitor

    def join_dicts(self):
        """chain(join) all dicts with post data for send to server for execute spiders"""
        dict_data = dict(chain(self.dict_arbitr().items(), self.dict_org_name().items(),
                               self.dict_debitor().items()))
        return dict_data


class CheckInfoBeforeSend(FormatDbDataToDict, GetDatabaseData):

    def __init__(self) -> None:
        super().__init__()
        self.conn = GetDatabaseData()

    def check_if_table_exists(self):
        """check if table with data for fedresurs is exists"""
        self.conn.mycursor.execute(f"""SELECT EXISTS(
            SELECT * FROM information_schema.tables 
            WHERE table_schema = '{DATABASE}' 
        AND table_name = '{TABLE}'
    )""")
        if self.conn.mycursor.fetchone()[0] == 1:
            return 1
        else:
            return None

    def check_len_values(self, kwargs: dict):
        """check if any values of dict have length bigger than zero"""
        return any(v for k, v in kwargs.items() if len(v) > 0)

    def check_for_any_data(self):
        """check if any data for post request for fedresurs spiders is exists. Return dict with data or None"""
        if self.check_if_table_exists():
            dict_data = self.join_dicts()
            if self.check_len_values(dict_data):
                return dict_data
            else:
                return None


async def message(data):
    async with websockets.connect(f'ws://{SERVER}:{PORT}') as s:
        msg = pickle.dumps(data)
        await s.send(msg)
        # await s.recv()


checker = CheckInfoBeforeSend()


def main():
    import time
    while True:
        time_sleep = 3 * 60
        time.sleep(time_sleep)
        checker.conn.create_connection()
        checker.create_connection()
        if checker.check_for_any_data():
            asyncio.get_event_loop().run_until_complete(message(checker.check_for_any_data()))
        checker.mycursor.close()
        checker.mydb.close()
        checker.conn.mycursor.close()
        checker.conn.mydb.close()


if __name__ == '__main__':
    logging.error(main())
