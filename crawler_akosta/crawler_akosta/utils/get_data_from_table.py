from mysql.connector import MySQLConnection, Error

from ..python_mysql_dbconfig import read_db_config
from .config import connect_db, format_parse_date

TABLE = connect_db['table']


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
        except Error as err:
            print(f"Error setting wait_timeout: {err}")

    def get_latest_lot(self):
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_id FROM {TABLE} where created_at >= "{format_parse_date(30, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            ids = list(map(lambda y: ''.join(y).strip(), (map(lambda x: x, set(data)))))
            return ids
        except Exception as e:
            print(e)
            return list()
