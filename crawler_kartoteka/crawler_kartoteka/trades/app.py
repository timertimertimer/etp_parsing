from crawler_kartoteka.crawler_kartoteka.locators.trade_locator import TradeLocator


class Combo:
    def __init__(self, response):
        self.response = response
        self.loc = TradeLocator

    @property
    def trading_type_and_form(self):
        type_, form = self.response.xpath(self.loc.trading_type_and_form_loc).strip().lower().split('/')
        if 'закрыт' in form:
            form = 'closed'
        elif 'открыт' in form:
            form = 'opened'
        else:
            ...
        if 'аукцион' in type_:
            type_ = 'auction'
        elif 'конкурс' in type_:
            type_ = 'competition'
        elif 'предложение' in type_:
            type_ = 'offer'
        else:
            ...
        return type_, form
