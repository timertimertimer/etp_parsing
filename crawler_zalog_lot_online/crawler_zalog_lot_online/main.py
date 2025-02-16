from scrapy.cmdline import execute


def rshb():
    execute(['scrapy', 'crawl', 'zalog_lot_online', '-a', 'domain=rshb'])


def sbrf():
    execute(['scrapy', 'crawl', 'zalog_lot_online', '-a', 'domain=sbrf'])


def rad():
    execute(['scrapy', 'crawl', 'zalog_lot_online', '-a', 'domain=rad'])


if __name__ == '__main__':
    rad()
