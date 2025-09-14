class SerpLocator:
    count_pagination_loc = '(//a[@class="end link"])[1]/text()'
    link_to_trade_loc = '//a[contains(@class, "search-comp-item")]/@href'
