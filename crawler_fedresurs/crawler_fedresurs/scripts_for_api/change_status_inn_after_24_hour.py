# -*- coding: utf-8 -*-
from mysql.connector import MySQLConnection, Error
from python_mysql_dbconfig import read_db_config
from datetime import datetime, timedelta
from invalid_data import invalid_inn

TABLE = 'fedres_data'


def format_parse_date():
    time_delta1 = timedelta(days=14)
    _date_now = datetime.now()
    _start_date = _date_now - time_delta1
    return _start_date.strftime("%Y-%m-%d %H:%M:%S")


def return_date_now():
    date_now = datetime.now()
    return date_now.strftime("%Y-%m-%d") + ' 00:00:00'


class ChangeStatusInTableTask:

    def __init__(self):
        self.db_config = read_db_config()
        self.conn = MySQLConnection(**self.db_config)
        self.mycursor = self.conn.cursor()

    def change_value(self):
        """
        change value if it was add less then 14 days ago
        from failed to active if condition right
        """
        new_set = set()
        self.mycursor.execute(
            f"""SELECT search_string FROM {TABLE} where type='debtor' and status='failed' and created_at >= '{format_parse_date()}' and created_at < '{return_date_now()}' """
        )
        records = self.mycursor.fetchall()
        for inn in records:
            if inn[0] not in invalid_inn:
                try:
                    check_set = set((inn[0].replace('0', '').strip()))
                    if (len(inn[0]) == 12 and len(check_set) > 3) or (len(inn[0]) == 10 and len(check_set) > 2):
                        new_set.add(inn[0])
                except:
                    continue
        for i in new_set:
            sqlStuff = f""" UPDATE {TABLE} SET status='active' where type='debtor' and status='failed' and search_string='{i}' """
            self.mycursor.execute(sqlStuff)
        self.conn.commit()
        self.mycursor.close()
        self.conn.close()
        return 0


worker = ChangeStatusInTableTask()


def main():
    return worker.change_value()


if __name__ == '__main__':
    main()
