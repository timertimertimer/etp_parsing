class LocatorSpider:
    count_lots_page_loc = '//span[text()="Найдено лотов"]/following-sibling::span[1]/text()'
    statistics_loc = '//div[@content="node:statistic"][1]'
    header_pagination_list_loc = '//select[@id="headerPagerSelect"]/preceding-sibling::span'
    trading_type_loc = '//tr//td[contains(text(),"Форма торгов")]/following-sibling::td[1]'

    # querySelectors
    fill_time_from = "document.querySelector('input[name=PublicDateMin]').value={}"
    fill_time_to = "document.querySelector('input[name=PublicDateMax]').value={}"
