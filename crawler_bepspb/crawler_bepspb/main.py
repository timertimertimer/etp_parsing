from scrapy.cmdline import execute


def bepspb():
    execute(['scrapy', 'crawl', 'bepspb'])


def bepspb_competition():
    execute(['scrapy', 'crawl', 'bepspb_competition'])


def bepspb_offer():
    execute(['scrapy', 'crawl', 'bepspb_offer'])


if __name__ == '__main__':
    bepspb()
