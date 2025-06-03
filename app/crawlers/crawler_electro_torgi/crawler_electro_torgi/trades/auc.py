from bs4 import BeautifulSoup

from general_utils import format_time


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
            date = BeautifulSoup(date, 'lxml').get_text().strip()
            return format_time(date)

    @property
    def end_date_trading(self):
        date = self.response.xpath(
            '//div[contains(normalize-space(text()), "Подведение итогов")]/following-sibling::div[1]'
        ).get()
        if date:
            date = BeautifulSoup(date, 'lxml').get_text().strip()
            return format_time(date)