import mysql.connector

from ..python_mysql_dbconfig import read_db_config
from ..utils.config import connect_db, TABLE_ORGANIZER
import logging

logger = logging.getLogger(__name__)
DB_CONNECT = read_db_config()
# data for collaborate with database
TABLE = connect_db['table_fedres_data']
DATABASE = DB_CONNECT['database']
host = DB_CONNECT['host']
user = DB_CONNECT['user']
passwd = DB_CONNECT['password']


class SetValueDb:

    def __init__(self) -> None:
        self.create_connection()

    def create_connection(self):
        self.mydb = mysql.connector.connect(
            host=host,
            user=user,
            passwd=passwd,
            database=DATABASE,

        )
        self.mycursor = self.mydb.cursor()

    def change_status_organizer(self, type_, string, status):
        """select type  and search sting -> change value from active to failed"""
        try:
            self.mycursor.execute(
                f"""UPDATE {TABLE} SET status='{status}' where type='{type_}'
                    and search_string='{string}';""")
            self.mydb.commit()
        except:
            self.mycursor.execute(
                f"""UPDATE {TABLE} SET status='{status}' where type='{type_}'
                                and search_string="{string}";""")
            self.mydb.commit()

    def get_and_set_id_organizer(self, inn_, string, type_, table_):
        """get value of id from main table and type it to task table"""
        try:
            self.mycursor.execute(
                f"""SELECT id FROM {table_} where inn={inn_}""")
            id_num = self.mycursor.fetchone()
        except:
            return None

        try:
            self.mycursor.execute(
                f"""UPDATE {TABLE} SET parsed_entity_id='{id_num[0]}' where type='{type_}'
                                and search_string='{string}';"""
            )
            self.mydb.commit()
        except:
            self.mycursor.execute(
                f"""UPDATE {TABLE} SET parsed_entity_id='{id_num[0]}' where type='{type_}'
                                            and search_string="{string}";"""
            )
            self.mydb.commit()
