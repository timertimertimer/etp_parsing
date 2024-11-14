from scrapy.cmdline import execute


def sberbank():
    execute(['scrapy', 'crawl', 'sberbank'])


def sberbank_playwright():
    execute(['scrapy', 'crawl', 'sberbank_playwright'])


def sberbank_new():
    execute(['scrapy', 'crawl', 'sberbank_new'])


if __name__ == '__main__':
    # sberbank()
    # sberbank_playwright()
    sberbank_new()
