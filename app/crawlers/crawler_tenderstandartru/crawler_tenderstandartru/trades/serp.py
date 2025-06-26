from .libraries import *

logger = logging.getLogger(__name__)


class SerpParse:
    def __init__(self, response_):
        self.response = response_
        self.soup = soup(self.response)

    def get_length_param(self):
        """get one of param data for request - Length"""
        form_ = self.soup.find(
            "form", attrs={"action": re.compile(r"/Trade/AllSearch\?Length")}
        )
        if form_:
            length = str(form_.get("action")).strip()
            number = "".join(re.findall(r"\d+$", length))
            return number

    def get_types_param(self) -> str:
        """get one of param data for request - types value, flot number - return string"""
        type_value = self.soup.find("input", id="types")
        if type_value:
            return str(type_value["value"])

    def get_next_page_link(self, current_page: str, data_origin_):
        """check if next page exists if true - return full link"""
        next_page = self.soup.find_all(
            "a", attrs={"data-ajax-complete": "OnPagerLinkComplete"}
        )
        if len(next_page) > 0:
            next_page_number = list(
                {x for x in next_page if x.get_text().strip() == str(current_page)}
            )
            if len(next_page_number) == 1:
                _href = next_page_number[0].get("href")
                full_url = re.sub(r"/$", "", data_origin_) + _href
                return full_url

    def get_status(self, status_text):
        """return status"""
        active = ("прием заявок",)
        pending = ("подтвержден", "ожидание начала торгов")
        ended = (
            "отклонен",
            "идет торг",
            "торг завершен",
            "завершен",
            "приостановлен",
            "ожидание подтверждения",
            "обработка заявок",
            "торг не состоялся",
            "зависит от лота",
            "отменен организатором",
        )
        if dedent_func(str(status_text).lower()) in active:
            return "active"
        elif dedent_func(str(status_text).lower()) in pending:
            return "pending"
        elif dedent_func(str(status_text).lower()) in ended:
            return "ended"
        else:
            logger.error(f"{self.response.url} :: STATUS ERROR {status_text}")

    def get_div_with_lots(self):
        """return block div with data of trading pages and lots"""
        id_divTradesTable = self.soup.find("div", class_="items-list")
        if id_divTradesTable:
            return id_divTradesTable

    def get_table_with_lots(self):
        id_tradesTable = self.soup.find("table", class_="trades_table")
        if id_tradesTable:
            return id_tradesTable

    def get_lots_data_from_div_table(self, crawler_name: str):
        """fetch data (trading_link, lot_link, lot_number, organizer, status)"""
        if _div := self.get_div_with_lots():
            short_lot_data = list()
            for lot_data in _div.find_all("div", class_="row item-row"):
                trading_link = lot_data.find(href=re.compile(r"/Trade/View/\d+$"))
                if trading_link:
                    trading_link = re.sub(
                        r"/$", "", data_origin[crawler_name]
                    ) + trading_link.get("href")
                lot_link = lot_data.find(href=re.compile(r"/TradeLot/View/\d+$"))
                if lot_link:
                    lot_link = re.sub(
                        r"/$", "", data_origin[crawler_name]
                    ) + lot_link.get("href")
                lot_number = lot_data.find("span", class_="item-number")
                if lot_number:
                    lot_number = lot_number.get_text().replace("№", "").strip()
                organizer = lot_data.find(
                    "label", string=re.compile(r"Организатор торгов", re.IGNORECASE)
                )
                if organizer:
                    _a_tag = organizer.findNextSibling("a")
                    if _a_tag:
                        organizer = re.sub(r"^ИП", "", _a_tag.get_text().strip())
                status_main = lot_data.find(
                    "label", string=re.compile(r"Статус", re.IGNORECASE)
                )
                status = None
                if status_main:
                    status = status_main.next_sibling.strip()
                    if len(status) == 0:
                        status = status_main.findNext("span")
                        if status:
                            status = status.get_text()
                start_price = lot_data.find(
                    "label", string=re.compile(r"Начальная цена", re.IGNORECASE)
                )
                if start_price:
                    start_price = start_price.next_sibling.strip()
                    if start_price:
                        start_price = make_float(start_price)
                start_date_trading = lot_data.find(
                    "label", string=re.compile(r"Дата проведения", re.IGNORECASE)
                )
                if start_date_trading:
                    try:
                        start_date_trading = format_time_period(
                            start_date_trading.next_sibling.strip()
                        )
                    except Exception as e:
                        print(e)
                        start_date_trading = None
                short_lot_data.append(
                    (
                        trading_link,
                        lot_link,
                        lot_number,
                        organizer,
                        status,
                        start_price,
                        start_date_trading,
                    )
                )
            return deque(short_lot_data)

    def get_lots_data_from_table(self, _data_origin):
        table = self.get_table_with_lots()
        if not table:
            return []
        lots = []
        try:
            for lot_data in table.find_all("tr")[1:]:
                lot_data_splitted = lot_data.find_all("td")
                trading_link = UrlConfig.url_join(
                    _data_origin, lot_data_splitted[0].find("a").get("href")
                )
                lot_number = lot_data_splitted[2].get_text().strip()
                lot_link = UrlConfig.url_join(
                    _data_origin, lot_data_splitted[3].find("a").get("href")
                )
                status = lot_data_splitted[-2].get_text().strip()
                lots.append((trading_link, lot_link, lot_number, status))
            return lots
        except Exception:
            pass

    def get_trading_id(self, trading_url):
        """return last number of trading link"""
        return "".join(re.findall(r"\d+$", trading_url.strip()))

    def get_trading_type(self):
        """return trading type"""
        if re.match(".+Trade/AuctionTrades.?", str(self.response.url)):
            return "auction"
        elif re.match(".+Trade/PublicOfferTrades.?", str(self.response.url)):
            return "offer"
        elif re.match(".+Trade/CompetitionTrades.?", str(self.response.url)):
            return "competition"
        else:
            logger.error(
                f"{self.response.url} :: ERROR {self.get_trading_type.__name__} {self.response.url}"
            )
