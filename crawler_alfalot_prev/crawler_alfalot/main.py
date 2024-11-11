from scrapy.cmdline import execute


def alfalot():
    execute(['scrapy', 'crawl', 'alfalot'])


def alfalot_offer():
    execute(['scrapy', 'crawl', 'alfalot_offer'])


def alfalot_competition():
    execute(['scrapy', 'crawl', 'alfalot_competition'])


if __name__ == '__main__':
    alfalot()
