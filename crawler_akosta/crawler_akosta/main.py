from scrapy.cmdline import execute


def akosta_new():
    execute(['scrapy', 'crawl', 'akosta_new'])


def akosta():
    execute(['scrapy', 'crawl', 'akosta'])

def akosta_full():
    execute(['scrapy', 'crawl', 'akosta_full'])


if __name__ == '__main__':
    akosta_full()
    