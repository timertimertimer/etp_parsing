from pathlib import Path

from app.utils.config import start_dates

data_origin_url = "https://utp.sberbank-ast.ru/"
main_url_start = "https://utp.sberbank-ast.ru/Bankruptcy/List/BidList"
part_path_to_trade = r"PurchaseView"
part_path_to_lot = r"BidView"
crawler_name = "sberbank"
start_date = start_dates[crawler_name]

main_urls = {
    "bankruptcy": "https://utp.sberbank-ast.ru/Bankruptcy",
    "fz223": "https://utp.sberbank-ast.ru/Trade",
    "fz44": "https://utp.sberbank-ast.ru/RussianPost",
    "capital_repair": "https://utp.sberbank-ast.ru/GKH",
    "legal_entities": {
        "cbrf": "https://utp.sberbank-ast.ru/CBRF",
        "rosatom": "https://utp.sberbank-ast.ru/Rosatom",
    },
    "commercial": {
        "transneft": "https://utp.sberbank-ast.ru/Transneft",
        "property": "https://utp.sberbank-ast.ru/Property",
    },
}

search_query_urls = {
    "bankruptcy": f"{main_urls['bankruptcy']}/SearchQuery/BidList",
    "fz223": f"{main_urls['fz223']}/SearchQuery/BidList",
    "fz44": f"{main_urls['fz44']}/SearchQuery/PurchaseList",
    "capital_repair": f"{main_urls['capital_repair']}/SearchQuery/PurchaseList",
    "legal_entities": {
        "cbrf": f"{main_urls['legal_entities']['cbrf']}/SearchQuery/PurchaseList",
        "rosatom": f"{main_urls['legal_entities']['rosatom']}/SearchQuery/BidList",
    },
    "commercial": {
        "transneft": f"{main_urls['commercial']['transneft']}/SearchQuery/PurchaseSalesList",
        "property": f"{main_urls['commercial']['property']}/SearchQuery/BidList",
    },
}

list_urls = {
    "bankruptcy": f"{main_urls['bankruptcy']}/List/BidList",
    "fz223": f"{main_urls['fz223']}/List/BidList",
    "fz44": f"{main_urls['fz44']}/List/PurchaseList",
    "capital_repair": f"{main_urls['capital_repair']}/List/PurchaseList",
    "legal_entities": {
        "cbrf": f"{main_urls['legal_entities']['cbrf']}/List/PurchaseList",
        "rosatom": f"{main_urls['legal_entities']['rosatom']}/List/BidList",
    },
    "commercial": {
        "transneft": f"{main_urls['commercial']['transneft']}/List/PurchaseSalesList",
        "property": f"{main_urls['commercial']['property']}/List/BidList",
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
first_part_link = "https://utp.sberbank-ast.ru/Bankruptcy/File/DownloadFile?fid="


def get_xml_request_data(prefix: str):
    with open(
        Path(__file__).parent.parent / "data" / f"{prefix}_request.xml",
        encoding="utf-8",
    ) as file:
        return file.read().replace("\n", "").replace(" ", "")
