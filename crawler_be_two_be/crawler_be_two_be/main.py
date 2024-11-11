from scrapy.cmdline import execute


def betwobe():
    execute(['scrapy', 'crawl', 'betwobe'])


def betwobe_comp():
    execute(['scrapy', 'crawl', 'betwobe_comp'])


def betwobe_offer():
    execute(['scrapy', 'crawl', 'betwobe_offer'])


if __name__ == '__main__':
    betwobe()
