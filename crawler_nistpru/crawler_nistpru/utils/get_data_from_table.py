from mysql.connector import MySQLConnection

from crawler_nistpru.python_mysql_dbconfig import read_db_config
from .config import tables, format_parse_date

TABLE = tables['table_nistp']


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self):
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_link, CONVERT(lot_number,char)  FROM {TABLE} where created_at >= "{format_parse_date(7, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            links = list(map(lambda y: ''.join(y).strip(), (map(lambda x: x, set(data)))))
            return links
        except Exception as e:
            print(e)
            return list()
