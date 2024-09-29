import re

from mysql.connector import MySQLConnection

from crawler_kartoteka_ru.python_mysql_dbconfig import read_db_config
from crawler_kartoteka_ru.utils.config import format_parse_date, tables

TABLE = tables['table_kartoteka']


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self, table=TABLE, day=7) -> list or None:
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT CONVERT(lot_number,char), lot_link FROM {table} where created_at >= "{format_parse_date(day, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            tup = tuple(map(lambda x: (x[0], re.sub(r'&_=\d+$', '', x[1])), map(lambda y: y, data)))
            return tup
        except Exception as e:
            print(e)
            return list()
