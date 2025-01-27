from mysql.connector import MySQLConnection

from general_utils import read_db_config
from general_utils.config import format_parse_date


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self):
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT lot_link FROM lots_sberbank where created_at >= "{format_parse_date(30, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            links = list(map(lambda y: ''.join(y).strip(), (map(lambda x: x, set(data)))))
            return links
        except Exception as e:
            print(e)
            self.curr.close()
            self.conn.close()
            return list()
