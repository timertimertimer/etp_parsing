from mysql.connector import MySQLConnection

from crawler_ruTrade24.python_mysql_dbconfig import read_db_config
from crawler_ruTrade24.config import db_connect, format_parse_date

TABLE = db_connect['table_name']


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self):
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_link FROM {TABLE} where created_at >= "{format_parse_date(30, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            data_lst = list(map(lambda x: ''.join(x), data))
            self.curr.close()
            self.conn.close()
            return data_lst
        except Exception as e:
            print(e)
            self.curr.close()
            self.conn.close()
            return list()
