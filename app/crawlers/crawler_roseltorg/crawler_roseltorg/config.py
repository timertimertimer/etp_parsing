from datetime import timedelta, datetime

from app.utils import (
    DateTimeHelper
)
from app.utils.config import start_dates

crawler_name = 'roseltorg'
start_date = start_dates[crawler_name]
search_link = "https://www.roseltorg.ru/procedures/search"
# https://www.roseltorg.ru/procedures/search?status%5B%5D=5&status%5B%5D=0&status%5B%5D=1&place=fkr capital_repair
# https://www.roseltorg.ru/procedures/search?sale=1&status%5B%5D=5&status%5B%5D=0&status%5B%5D=1&currency=all&source%5B%5D=28&source%5B%5D=2 fz223
# https://www.roseltorg.ru/procedures/search?sale=1&status%5B%5D=5&status%5B%5D=0&status%5B%5D=1&currency=all&source%5B%5D=20&source%5B%5D=24 legal_entities

formdatas = {
    'legal_entities': {"source[]": ["20", "24"], "currency": "all", "sale": "1", "status[]": ["5", "0", "1"]},
    'capital_repair': {'place': "fkr", "status[]": ["5", "0", "1"]},
    'fz223': {"source[]": ["28", "2"], "currency": "all", "sale": "1", "status[]": ["5", "0", "1"]},
}
data_origin = "https://www.roseltorg.ru/"
