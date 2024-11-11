from scrapy.cmdline import execute


def ausib_ru():
    execute(['scrapy', 'crawl', 'ausib_ru'])


def ptp_centr_ru():
    execute(['scrapy', 'crawl', 'ptp_centr_ru'])


def regtorg_com():
    execute(['scrapy', 'crawl', 'regtorg_com'])


def etp_profit_ru():
    execute(['scrapy', 'crawl', 'etp_profit_ru'])


def seltim_ru():
    execute(['scrapy', 'crawl', 'seltim_ru'])


def atctrade_ru():
    execute(['scrapy', 'crawl', 'atctrade_ru'])


def torgidv_ru():
    execute(['scrapy', 'crawl', 'torgidv_ru'])


def aukcioncenter():
    execute(['scrapy', 'crawl', 'aukcioncenter'])


if __name__ == '__main__':
    torgidv_ru()
