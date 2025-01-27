from mysql.connector import MySQLConnection

from general_utils import read_db_config


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self):
        try:
            self.curr.execute(
                f""" SELECT trading_link FROM lots_heveya where created_at >= "{format_parse_date(30, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            links = list(map(lambda y: ''.join(y).strip(), (map(lambda x: x, set(data)))))
            return links
        except Exception as e:
            print(e)
            return list()
