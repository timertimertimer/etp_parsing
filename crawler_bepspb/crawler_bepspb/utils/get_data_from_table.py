from mysql.connector import MySQLConnection

from crawler_bepspb.python_mysql_dbconfig import read_db_config
from crawler_bepspb.utils.config import format_parse_date, tables

TABLE = tables['table_bepspb']


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self, table=TABLE, day=1) -> list or None:
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT trading_link, CONVERT(lot_number,char), lot_link FROM {table} where created_at >= "{format_parse_date(day, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            return data
        except Exception as e:
            print(e)
            return list()