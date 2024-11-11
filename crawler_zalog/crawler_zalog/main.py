from scrapy.cmdline import execute

def zalog_ross():
    execute(['scrapy', 'crawl', 'zalog_ross'])


def zalog_sber():
    execute(['scrapy', 'crawl', 'zalog_sber'])


if __name__ == '__main__':
    zalog_sber()