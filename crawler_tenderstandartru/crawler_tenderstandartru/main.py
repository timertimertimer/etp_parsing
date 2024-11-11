from scrapy.cmdline import execute


def tenderstandartru():
    execute(['scrapy', 'crawl', 'tenderstandartru'])


def tenderstandartru_offer():
    execute(['scrapy', 'crawl', 'tenderstandartru_offer'])


if __name__ == '__main__':
    tenderstandartru()
