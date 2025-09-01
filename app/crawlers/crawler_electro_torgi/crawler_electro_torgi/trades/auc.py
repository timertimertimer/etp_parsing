from bs4 import BeautifulSoup

from app.utils import DateTimeHelper


class Auc:
    def __init__(self, response):
        self.response = response

    @property
    def start_date_trading(self):
        date = self.response.xpath(
            '//div[contains(normalize-space(text()), "Дата проведения торгов") or '
            'contains(normalize-space(text()), "Прием ценовых предложений")]/following-sibling::div[1]'
        ).get()
        if date:
            date = BeautifulSoup(date, "lxml").get_text().strip()
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        return None

    @property
    def end_date_trading(self):
        date = self.response.xpath(
            '//div[contains(normalize-space(text()), "Подведение итогов")]/following-sibling::div[1]'
        ).get()
        if date:
            date = BeautifulSoup(date, "lxml").get_text().strip()
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        return None
