from scrapy.cmdline import execute


def rad():
    execute(['scrapy', 'crawl', 'lot_online', '-a', 'domain=rad'])


def confiscate():
    execute(['scrapy', 'crawl', 'lot_online', '-a', 'domain=confiscate'])


def lease():
    execute(['scrapy', 'crawl', 'lot_online', '-a', 'domain=lease'])


def privatization():
    execute(['scrapy', 'crawl', 'lot_online', '-a', 'domain=privatization'])


def arrested():
    execute(['scrapy', 'crawl', 'lot_online', '-a', 'domain=arrested'])


if __name__ == '__main__':
    rad()
