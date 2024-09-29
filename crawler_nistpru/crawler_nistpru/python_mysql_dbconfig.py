from configparser import ConfigParser
from os import environ
from pathlib import PurePosixPath

from scrapy.utils.conf import closest_scrapy_cfg

proj_root = closest_scrapy_cfg()
project_main_dir = PurePosixPath(proj_root).parent.parent.name + '/'
_path = f'{environ["HOME"]}/{project_main_dir}config.ini'
print(_path)

def read_db_config(filename=_path, section='mysql'):
    """ Read database configuration file and return a dictionary object
    :param filename: name of the configuration file
    :param section: section of database configuration
    :return: a dictionary of database parameters
    """
    # create parser and read ini configuration file
    parser = ConfigParser()
    parser.read(filename)
    # get section, default to mysql
    db = {}
    if parser.has_section(section):
        items = parser.items(section)
        for item in items:
            db[item[0]] = item[1]
    else:
        raise Exception('{0} not found in the {1} file'.format(section, filename))

    return db