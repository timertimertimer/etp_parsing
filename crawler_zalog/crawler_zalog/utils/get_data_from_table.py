import mysql
from mysql.connector import MySQLConnection

from ..python_mysql_dbconfig import read_db_config
from crawler_zalog.utils.config import format_parse_date, db_tables

TABLE = db_tables['zalog_sber']


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.set_wait_timeout(600)

    def set_wait_timeout(self, timeout):
        """Устанавливает wait_timeout для текущей сессии."""
        try:
            self.curr.execute(f"SET SESSION wait_timeout = {timeout};")
            print(f"Session wait_timeout set to {timeout} seconds.")
        except mysql.connector.Error as err:
            print(f"Error setting wait_timeout: {err}")

    def get_latest_lot(self, table=TABLE, day=3) -> list or None:
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_link FROM {table} where created_at >= "{format_parse_date(day, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            return data
        except Exception as e:
            print(e)
            return list()
