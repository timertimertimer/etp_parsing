import csv

from general_utils.db import get_db
from general_utils.models import Region, Address, TradingFloor
from general_utils.config import data_path
from general_utils.models.city import City



if __name__ == '__main__':
    add_cities()
