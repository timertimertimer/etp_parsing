from scrapy.cmdline import execute


def bankrot_cdtrf():
    execute(['scrapy', 'crawl', 'bankrot_cdtrf'])


if __name__ == '__main__':
    bankrot_cdtrf()
