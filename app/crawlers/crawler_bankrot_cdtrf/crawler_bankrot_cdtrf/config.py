from datetime import timedelta, datetime

from app.utils.config import (
    DateTimeHelper,
)

data_origin_url = "https://cdtrf.ru/"
trade_page = "https://bankrot.cdtrf.ru/public/undef/card/tradel.aspx"
trade_page_file = "https://bankrot.cdtrf.ru/public/undef/card/"

trade_type_offer = "3"
trade_auction = "1"
trade_competition_ = "2"
start_date = DateTimeHelper.format_datetime(datetime.now() - timedelta(days=3), '%d.%m.%Y')
