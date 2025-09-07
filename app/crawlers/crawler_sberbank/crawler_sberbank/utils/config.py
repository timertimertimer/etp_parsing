from datetime import datetime, timedelta
from pathlib import Path

from app.utils.config import start_dates

data_origin_url = "https://utp.sberbank-ast.ru/"
main_url_start = "https://utp.sberbank-ast.ru/Bankruptcy/List/BidList"
part_path_to_trade = r"PurchaseView"
part_path_to_lot = r"BidView"
crawler_name = "sberbank"
start_date = start_dates[crawler_name]

search_query_urls = {
    "bankruptcy": "https://utp.sberbank-ast.ru/Bankruptcy/SearchQuery/BidList",
    "fz223": "https://utp.sberbank-ast.ru/Trade/SearchQuery/BidList",
    "fz44": "https://utp.sberbank-ast.ru/RussianPost/SearchQuery/PurchaseList",
    "capital_repair": "https://utp.sberbank-ast.ru/GKH/SearchQuery/PurchaseList",
    "legal_entities": {
        "cbrf": "https://utp.sberbank-ast.ru/CBRF/SearchQuery/PurchaseList",
        "rosatom": "https://utp.sberbank-ast.ru/Rosatom/SearchQuery/BidList",
    },
    "commercial": {
        "transneft": "https://utp.sberbank-ast.ru/Transneft/SearchQuery/PurchaseSalesList",
        "property": "https://utp.sberbank-ast.ru/Property/SearchQuery/BidList",
    },
}

urls = {
    "bankruptcy": "https://utp.sberbank-ast.ru/Bankruptcy/List/BidList",
    "fz223": "https://utp.sberbank-ast.ru/Trade/List/BidList",
    "fz44": "https://utp.sberbank-ast.ru/RussianPost/List/PurchaseList",
    "capital_repair": "https://utp.sberbank-ast.ru/GKH/List/PurchaseList",
    "legal_entities": {
        "cbrf": "https://utp.sberbank-ast.ru/CBRF/List/PurchaseList",
        "rosatom": "https://utp.sberbank-ast.ru/Rosatom/List/BidList",
    },
    "commercial": {
        "transneft": "https://utp.sberbank-ast.ru/Transneft/List/PurchaseSalesList",
        "property": "https://utp.sberbank-ast.ru/Property/List/BidList",
    },
}
api_map = {
    "bankruptcy": True,
    "fz223": False,
    "fz44": False,
    "capital_repair": True,
    "legal_entities": True,
    "commercial": False,
}
# format period
# W - week
# D - day
format_period = "D"
# periods - how many weeks or days been iteration - FREQUENCY (freq)
periods_ = 1
pattern_lots_links = r" <objectHrefTerm>(.*?)</objectHrefTerm>"
first_part_link = (
    "https://utp.sberbank-ast.ru/Bankruptcy/File/DownloadFile?fid="  # FIXME
)


def get_xml_request_data(prefix: str):
    with open(
        Path(__file__).parent.parent / "data" / f"{prefix}_request.xml",
        encoding="utf-8",
    ) as file:
        return file.read().replace("\n", "").replace(" ", "")
