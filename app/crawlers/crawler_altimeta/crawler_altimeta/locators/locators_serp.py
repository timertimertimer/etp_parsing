class LocatorSerp:
    links_to_the_next_page = (
        r'//tr/td[contains(., "Страницы")]/strong/following-sibling::a/@href'
    )
    links_to_trade_page = '//table[@class="data"]//tr[contains(@onclick, "if")]'
