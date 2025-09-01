from datetime import timedelta, datetime

from app.utils.config import DateTimeHelper

start_date = DateTimeHelper.format_datetime(datetime.now() - timedelta(days=30), "%d.%m.%Y %H:%M")

data_origin = {
    "au_pro": "https://au-pro.ru/",
    "tenderstandart": "https://tenderstandart.ru/",
    "torggroup": "https://bankrot.torggroup.org/",
    "viomitra": "https://bankrot.viomitra.ru/",
}

trades = ["Trade/AuctionTrades", "Trade/PublicOfferTrades", "Trade/CompetitionTrades"]

tables = {
    "au_pro": "lots_au_pro",
    "tenderstandart": "lots_tenderstandart",
    "torggroup": "lots_torggroup",
    "viomitra": "lots_viomitra",
}

search_param = {
    "Length": "",
    "types": "",
    "LotNumber": "",
    "OrganizerName": "",
    "OrganizerINN": "",
    "OrganizerKPP": "",
    "OrganizerAddress": "",
    "TradeId": "",
    "TradeName": "",
    "BasePrice": "",
    "IsOpenPriceForm": "",
    "TradePeriodStart": start_date,
    "TradePeriodEnd": "",
    "LotStateId": "",
    "LotName": "",
    "X-Requested-With": "XMLHttpRequest",
    "_": "",
}
