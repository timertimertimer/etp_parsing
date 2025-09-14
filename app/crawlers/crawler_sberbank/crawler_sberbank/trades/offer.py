import re
from bs4 import BeautifulSoup as BS

from app.utils import dedent_func, logger, DateTimeHelper
from app.db.models import DownloadData
from ..utils.config import main_urls
from ..utils.manage_spider import deep_get_dict


class OfferParse:
    def __init__(self, data, url):
        self.url = url
        self.data = data

    @property
    def get_periods(self):
        try:
            data = deep_get_dict(self.data, "BidView.BidReductionPeriod.Periods")
        except Exception as e:
            return None
        periods = []
        for period in data:
            start = period["PeriodStartDate"]
            end = period["PeriodEndDate"]
            price = re.sub(r"\s", "", period["BidAmount"])
            period = {
                "start_date_requests": DateTimeHelper.smart_parse(start).astimezone(
                    DateTimeHelper.moscow_tz
                ),
                "end_date_requests": DateTimeHelper.smart_parse(end).astimezone(
                    DateTimeHelper.moscow_tz
                ),
                "end_date_trading": DateTimeHelper.smart_parse(end).astimezone(
                    DateTimeHelper.moscow_tz
                ),
                "current_price": round(float(price), 2),
            }
            periods.append(period)
        return periods

    @property
    def start_date_request(self):
        periods = self.get_periods
        try:
            return periods[0]["start_date_requests"]
        except Exception as e:
            logger.error(f"{self.url} :: INVALID DATA START DATE REQUEST OFFER")
        return None

    @property
    def end_date_request(self):
        periods = self.get_periods
        try:
            return periods[-1]["end_date_requests"]
        except Exception as e:
            logger.error(f"{self.url} :: INVALID DATA END DATE REQUEST OFFER")
        return None

    @property
    def start_date_trading(self):
        return self.start_date_request

    @property
    def end_date_trading(self):
        return self.end_date_request

    @property
    def start_price(self):
        start_price = deep_get_dict(self.data, "BidView.Bids.BidTenderInfo.BidPrice")
        start_price = re.sub(r"\s", "", start_price)
        pattern = re.compile(r"\d+\.\d{1,2}")
        try:
            start_price = dedent_func(
                BS(str(start_price), features="lxml").get_text()
            ).strip()
            if start_price:
                return round(float("".join(pattern.findall(start_price)[0])), 2)
        except Exception as e:
            logger.error(f"{self.url} :: INVALID DATA START PRICE OFFER")
        return None

    def get_xml_data(self, xml_data: str):
        return xml_data

    def get_file_name_and_hash(
        self, lst_file_name, property_type: str, org: str = None
    ):
        if isinstance(lst_file_name, dict):
            lst_file_name = [lst_file_name]
        clean_name = list()
        lst_hash_links = list()
        for n in lst_file_name:
            clean_name.append(n["filename"])
            main_url = main_urls[property_type]
            if org:
                main_url = main_url[org]
            lst_hash_links.append(f"{main_url}/File/DownloadFile?fid={n['fileid']}")
        names = clean_name
        links = lst_hash_links
        return names, links

    def download(self, file, property_type: str, org: str):
        files = list()
        name, link = self.get_file_name_and_hash(file, property_type, org)
        for i in range(len(name)):
            files.append(DownloadData(url=link[i], file_name=name[i], referer=self.url))
        return files
