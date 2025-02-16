import mysql
from mysql.connector import MySQLConnection

from general_utils import read_db_config
from general_utils.config import format_parse_date


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

    def get_latest_lot(self, day=30) -> list or None:
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_link FROM lots_zalog_lot_online where created_at >= "{format_parse_date(day, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            return data
        except Exception as e:
            print(e)
            return list()
