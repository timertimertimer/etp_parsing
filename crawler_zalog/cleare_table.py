
from mysql.connector import MySQLConnection, Error

from crawler_zalog.python_mysql_dbconfig import read_db_config
from crawler_zalog.utils.config import db_tables

TABLE = db_tables['zalog_sber']

db_config = read_db_config()
conn = MySQLConnection(**db_config)
curr = conn.cursor()

try:
    Delete_all_rows = f"""truncate table {TABLE} """
    curr.execute(Delete_all_rows)
    conn.commit()
    print("All Record Deleted successfully ")

except Error as error:
    print("Failed to Delete all records from database table: {}".format(error))
finally:
    if conn.is_connected():
        curr.close()
        conn.close()
        print("MySQL connection is closed")
