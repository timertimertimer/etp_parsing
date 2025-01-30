from scrapy.cmdline import execute


def run_scrapy(category, subcategory):
    execute(['scrapy', 'crawl', 'lot_online_zalog', '-a', f'category={category}', '-a', f'subcategory={subcategory}'])


if __name__ == '__main__':
    run_scrapy('movable_property', 'cars')
    # run_scrapy('movable_property', 'equipment')
    # run_scrapy('movable_property', 'others')
    #
    # run_scrapy('not_movable_property', 'homes')
    # run_scrapy('not_movable_property', 'ground')
    # run_scrapy('not_movable_property', 'others')
    # run_scrapy('not_movable_property', 'commercial')
    #
    # run_scrapy('financial_assets', 'agreements')
    # run_scrapy('financial_assets', 'material')
    # run_scrapy('financial_assets', 'securities')
    # run_scrapy('financial_assets', 'cesia')
