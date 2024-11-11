from scrapy.cmdline import execute


def mets():
    execute(['scrapy', 'crawl', 'mets'])


def mets_playwright():
    execute(['scrapy', 'crawl', 'mets-playwright'])


if __name__ == '__main__':
    # mets()
    mets_playwright()
