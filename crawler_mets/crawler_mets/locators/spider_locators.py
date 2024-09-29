class LocatorSpider:
    sid_loc = '//span[@class="sid"]'
    count_pagination_loc = '//div[@class="resholder"]/following-sibling::div//a[last()]/text()'
    link_to_trade_loc = '//a[contains(@href, "generalView")]'
    trading_type_loc = '//td[contains(.,"Тип торгов")]/following-sibling::td[1]'

