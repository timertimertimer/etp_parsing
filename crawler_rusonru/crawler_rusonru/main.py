from scrapy.cmdline import execute


def ruson():
    execute(['scrapy', 'crawl', 'ruson'])


def eltorg():
    execute(['scrapy', 'crawl', 'eltorg'])


def nistp():
    execute(['scrapy', 'crawl', 'nistp'])


def promkonsalt():
    execute(['scrapy', 'crawl', 'promkonsalt'])


if __name__ == '__main__':
    eltorg()
