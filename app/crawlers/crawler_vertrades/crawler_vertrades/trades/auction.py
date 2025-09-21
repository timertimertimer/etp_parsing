import re

from bs4 import BeautifulSoup

from app.utils import DateTimeHelper, contains, dedent_func, logger


class AuctionParse:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(self.response.text, "lxml")

    @property
    def start_date_trading(self):
        date = self.soup.find(
            "td", text=contains("Начало подачи предложений о цене имущества")
        )
        if date:
            return DateTimeHelper.smart_parse(
                date.find_next_sibling("td").get_text()
            ).astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def end_date_trading(self):
        date = self.soup.find(
            "td", text=contains("Дата и время подведения результатов торгов")
        )
        if date:
            return DateTimeHelper.smart_parse(
                date.find_next_sibling("td").get_text()
            ).astimezone(DateTimeHelper.moscow_tz)
        return None

    def step_price(self, lot):
        try:
            p = BeautifulSoup(str(lot), "lxml").find(
                "td", text=contains("Величина повышения")
            )
            if p:
                p = p.find_next_sibling("td")
                p = re.sub(
                    r"\s", "", dedent_func(p.get_text().strip()).replace(",", ".")
                )
                p = re.search(r"\d+(?:\.\d{1,2})?(?=руб)", p).group()
                if len(p) > 0:
                    return round(float(p), 2)
        except ValueError as e:
            logger.error(f"{self.response.url} :: INVALID DATA STEP PRICE\n{e}")
        return None
