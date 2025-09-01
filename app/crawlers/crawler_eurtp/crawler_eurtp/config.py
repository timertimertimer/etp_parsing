from datetime import datetime

from app.utils.config import DateTimeHelper

data_origin_url = "http://eurtp.ru/"
end_date = DateTimeHelper.format_datetime(datetime.now(), '%d.%m.%Y')
page_limit = 10
bankrupt_categories = [
    "https://eurtp.ru/Home/AuctionOpen",
    "https://eurtp.ru/Home/AuctionClose",
    "https://eurtp.ru/Home/Competition",
    "https://eurtp.ru/Home/PublicOffering",
]
arrested_categories = [
    "http://eurtp.ru/Home/AuctionArrested",
    "http://eurtp.ru/Home/ArrestedClose",
]
