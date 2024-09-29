from mysql.connector import MySQLConnection

from crawler_altimeta.python_mysql_dbconfig import read_db_config
from crawler_altimeta.utils.config import format_parse_date


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self, table, day=1) -> list or None:
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_link FROM {table} where created_at >= "{format_parse_date(day, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            links = list(map(lambda y: ''.join(y).strip(), (map(lambda x: x, set(data)))))
            return links
        except Exception as e:
            print(e)
            return None

    def get_latest_lot_id(self, table, day=1) -> list or None:
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_id FROM {table} where created_at >= "{format_parse_date(day, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            links = list(map(lambda y: ''.join(y).strip(), (map(lambda x: x, set(data)))))
            return links
        except Exception as e:
            print(e)
            return None
