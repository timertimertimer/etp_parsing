class SerpLocator:
    trade_card_loc = '//div[@class="js-masonry-layout marketplace-commercial"]'
    link_to_trade_loc = (
        './/a[@class="marketplace-commercial__name"]/@href'  # Добавлена точка
    )
    status_loc = (
        './/p[@class="marketplace-commercial__seller-status"]/text()'  # Добавлена точка
    )
    short_name_loc = (
        './/a[@class="marketplace-commercial__name"]/text()'  # Добавлена точка
    )
    pagination_loc = '//div[@class="page-pagination__wrapper d-flex"]'
    next_page_loc = '//button[@class="nextPage js-pagination-next hidden"]/@value'
