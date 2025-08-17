from datetime import datetime, timedelta

from app.utils import DateTimeHelper

start_date = DateTimeHelper.format_datetime(
    datetime.now(DateTimeHelper.moscow_tz) - timedelta(days=1), "%Y-%m-%d"
)
formdata = {
    "lotStatus": "PUBLISHED,APPLICATIONS_SUBMISSION",
    "matchPhrase": "false",
    "pubFrom": start_date,
    "byFirstVersion": "true",
    "withFacets": "true",
    "size": "10",
    "page": "1",
    "sort": "firstVersionPublicationDate,desc",
}

data_origin = "https://torgi.gov.ru/"
search_link = "https://torgi.gov.ru/new/api/public/notices/search"
trade_link = "https://torgi.gov.ru/new/api/public/notices/noticeNumber"
