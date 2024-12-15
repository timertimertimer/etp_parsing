from mysql.connector import MySQLConnection

from ..python_mysql_dbconfig import read_db_config
from .config import format_parse_date, tables


class DbConnectCheckLots(object):

    def __init__(self, spider):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()
        self.table = tables[spider]

    def get_latest_lot(self):
        try:
            self.curr.execute(
                f""" SELECT trading_id FROM {self.table} where created_at >= "{format_parse_date(30, '%Y-%m-%d %H:%M:%S')}" """
            )
            data = self.curr.fetchall()
            links = list(map(lambda y: ''.join(y).strip(), (map(lambda x: x, set(data)))))
            return links
        except Exception as e:
            print(e)
            return list()
