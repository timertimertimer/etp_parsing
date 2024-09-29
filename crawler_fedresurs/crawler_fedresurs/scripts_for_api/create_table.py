from configparser import ConfigParser
from datetime import datetime
from os import getcwd
from pathlib import Path, PosixPath

from mysql.connector import MySQLConnection

from crawler_fedresurs.crawler_fedresurs.utils.config import home_dir

__path_config_ini = f'/home/parser/etp_parsing'
__config_ini = 'config.ini'
mysql_configure_file = Path(__path_config_ini, __config_ini)


table = 'fedres_data'

default_status = 'active'

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
class ConnectDB:
    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

dbins = ConnectDB()

def return_parse_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')


dbins.curr.execute(f"""CREATE TABLE IF NOT EXISTS {table}(
    id BIGINT AUTO_INCREMENT PRIMARY KEY, parsed_entity_id BIGINT, type VARCHAR(255), search_string VARCHAR(500), status VARCHAR(7), 
    created_at timestamp, CONSTRAINT CK_{table} UNIQUE (type, search_string)
) """)

sqlStuff = f"""INSERT INTO {table} (type, search_string, status, created_at) VALUES (%s, %s, %s, %s) 
            ON DUPLICATE KEY UPDATE type=VALUES(type),
                                    search_string=VALUES(search_string),
                                    created_at=VALUES(created_at)"""


def add_debitor():
    lst_debitor = list()
    type_ = 'debtor'
    with open('debitor.txt', 'r') as f:
        lines = [line.rstrip() for line in f]
        lst_debitor.extend(lines)
        for inn in lst_debitor:
            record = (type_, inn, default_status, return_parse_date())
            dbins.curr.execute(sqlStuff, record)
            dbins.conn.commit()


# def add_arbitr():
#     lst_arbitor = list()
#     type_ = 'arbitrator'
#     with open('arbitr_name.txt', 'r') as f:
#         lines = [line.rstrip() for line in f]
#         lst_arbitor.extend(lines)
#         for inn in lst_arbitor:
#             record = (type_, inn, default_status, return_parse_date())
#             dbins.curr.execute(sqlStuff, record)
#             dbins.conn.commit()
#
#
# def add_org_name():
#     lst_org_name = list()
#     type_ = 'organizer'
#     with open('organizer_name.txt', 'r') as f:
#         lines = [line.rstrip() for line in f]
#         lst_org_name.extend(lines)
#         for inn in lst_org_name:
#             record = (type_, inn, default_status, return_parse_date())
#             dbins.curr.execute(sqlStuff, record)
#             dbins.conn.commit()
#

# def add_org_company():
#     lst_org_company = list()
#     type_ = 'organizer_company'
#     with open('organizer_company.txt', 'r') as f:
#         lines = [line.rstrip() for line in f]
#         lst_org_company.extend(lines)
#         for inn in lst_org_company:
#             record = (type_, inn, default_status, return_parse_date())
#             mycursor.execute(sqlStuff, record)
#             mydb.commit()


add_debitor()
# add_arbitr()
# add_org_name()


