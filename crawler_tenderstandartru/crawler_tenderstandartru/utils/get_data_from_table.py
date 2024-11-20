from mysql.connector import MySQLConnection

from crawler_tenderstandartru.python_mysql_dbconfig import read_db_config
from crawler_tenderstandartru.utils.config import tables, format_parse_date

class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self, table):
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_link, lot_link, status FROM {table} where created_at >= "{format_parse_date(10, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            self.curr.close()
            self.conn.close()
            return data
        except Exception as e:
            print(e)
            self.curr.close()
            self.conn.close()
            return list()