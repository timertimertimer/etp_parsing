import os
from pathlib import Path
from configparser import ConfigParser
from .config import config_path
from dotenv import load_dotenv

load_dotenv()


def read_db_config(filename=config_path, section='mysql'):
    db = {}
    if Path(config_path).exists():
        parser = ConfigParser()
        parser.read(filename)
        if parser.has_section(section):
            items = parser.items(section)
            for item in items:
                db[item[0]] = item[1]
        else:
            raise Exception('{0} not found in the {1} file'.format(section, filename))
    else:
        db['host'] = os.getenv('DB_HOST')
        db['database'] = os.getenv('DB_DATABASE')
        db['user'] = os.getenv('DB_USERNAME')
        db['password'] = os.getenv('DB_PASSWORD')
        db['port'] = os.getenv('DB_PORT')
    return db


if __name__ == '__main__':
    print(read_db_config())
