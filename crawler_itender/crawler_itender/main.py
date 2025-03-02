from scrapy.cmdline import execute


def arbitat():
    execute(['scrapy', 'crawl', 'arbitat'])


def zakazrf():
    execute(['scrapy', 'crawl', 'bankrot_zakazrf'])


def propertytrade():
    execute(['scrapy', 'crawl', 'propertytrade'])


def tendergarant():
    execute(['scrapy', 'crawl', 'tendergarant'])


def vertrades():
    execute(['scrapy', 'crawl', 'vertrades'])


def tender_one():
    execute(['scrapy', 'crawl', 'tender_one'])


def utender():
    execute(['scrapy', 'crawl', 'utender'])


def etpugra():
    execute(['scrapy', 'crawl', 'etpugra'])


def gloriaservice():
    execute(['scrapy', 'crawl', 'gloriaservice'])


def bankrupt_centrr():
    execute(['scrapy', 'crawl', 'bankrupt_centrr'])


def bankrupt_etpu():
    execute(['scrapy', 'crawl', 'bankrupt_etpu'])


def torgibankrot():
    execute(['scrapy', 'crawl', 'torgibankrot'])


def utpl():
    execute(['scrapy', 'crawl', 'utpl'])


def meta_invest():
    execute(['scrapy', 'crawl', 'meta_invest'])


def alfalot():
    execute(['scrapy', 'crawl', 'alfalot'])


def bepspb():
    execute(['scrapy', 'crawl', 'bepspb'])


def arbbitlot():
    execute(['scrapy', 'crawl', 'arbbitlot'])


def ets24():
    execute(['scrapy', 'crawl', 'ets24'])


def selt_online():
    execute(['scrapy', 'crawl', 'selt_online'])


if __name__ == '__main__':
    alfalot()
