from mysql.connector import MySQLConnection

from crawler_sberbank.python_mysql_dbconfig import read_db_config
from crawler_sberbank.utils.config import connect_db, format_parse_date

TABLE = connect_db['table']


class DbConnectCheckLots(object):

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.curr = self.conn.cursor()

    def get_latest_lot(self):
        """ fetch all lots that have been added for 2 days  """
        try:
            self.curr.execute(
                f""" SELECT lot_link FROM {TABLE} where created_at >= "{format_parse_date(7, '%Y-%m-%d %H:%M:%S')}" """)
            data = self.curr.fetchall()
            links = list(map(lambda y: ''.join(y).strip(), (map(lambda x: x, set(data)))))
            return links
        except Exception as e:
            print(e)
            self.curr.close()
            self.conn.close()
            return list()


