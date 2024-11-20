from scrapy.cmdline import execute


def au_pro():
    execute(['scrapy', 'crawl', 'au_pro'])


def tenderstandartru():
    execute(['scrapy', 'crawl', 'tenderstandartru'])


def torggroup():
    execute(['scrapy', 'crawl', 'torggroup'])


def viomitra():
    execute(['scrapy', 'crawl', 'viomitra'])


if __name__ == '__main__':
    # au_pro()
    # tenderstandartru()
    # torggroup()
    viomitra()
