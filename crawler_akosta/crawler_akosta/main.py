from scrapy.cmdline import execute


def akosta():
    execute(['scrapy', 'crawl', 'akosta'])


if __name__ == '__main__':
    akosta()
