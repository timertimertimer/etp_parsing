from scrapy.cmdline import execute


def bankruptcy():
    execute(['scrapy', 'crawl', 'lot_online_bankruptcy', '-a', 'domain=bankruptcy'])


def private_property():
    execute(['scrapy', 'crawl', 'lot_online_private_property', '-a', 'domain=private_property'])


if __name__ == '__main__':
    private_property()
