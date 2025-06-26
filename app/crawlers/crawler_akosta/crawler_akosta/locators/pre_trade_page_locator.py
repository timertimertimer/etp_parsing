class SearchLocator:
    link_to_serp_trades_loc = '//a[contains(., "Банкротное имущество")]'

    links_to_trade_pages_loc = '//div[@id="formMain:lotListTable"]//tr[@data-ri]'

    trading_number_loc = '//a[@id="{}"]'

    start_date_request = '//a[contains(text(), "{}")]/ancestor::tr[1]//td[7]/text()'
