from datetime import timedelta, datetime

from app.utils import (
    DateTimeHelper
)

start_date = DateTimeHelper.format_datetime(datetime.now() - timedelta(1), "%d.%m.%y")
search_link = "https://www.roseltorg.ru/search/sale"
property_types = ['legal_entities', 'capital_repair', 'fz223']
sections = {
    'legal_entities': ["20", "24"],
    'capital_repair': {'place': "fkr"},
    'fz223': ["28", "2"],
}
initial_formdata = {"start_date_published": start_date}
formdatas = {
    'legal_entities': {"source[]": el for el in ["20", "24"]},
    'capital_repair': {'place': "fkr"},
    'fz223': {"source[]": el for el in ["28", "2"]},
}
data_origin = "https://www.roseltorg.ru/"
