from app.utils.config import format_parse_date

data_origin_url = "http://eurtp.ru/"
end_date = format_parse_date(0)
page_limit = 10
bankrupt_categories = [
    "https://eurtp.ru/Home/AuctionOpen",
    "https://eurtp.ru/Home/AuctionClose",
    "https://eurtp.ru/Home/Competition",
    "https://eurtp.ru/Home/PublicOffering",
]
arrested_categories = [
    "http://eurtp.ru/Home/AuctionArrested",
    "http://eurtp.ru/Home/ArrestedClose"
]
