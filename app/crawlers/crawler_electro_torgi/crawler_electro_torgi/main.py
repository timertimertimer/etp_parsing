from scrapy.cmdline import execute


def electro_torgi():
    execute(['scrapy', 'crawl', 'electro_torgi'])


def uralbidin():
    execute(['scrapy', 'crawl', 'uralbidin'])


def vetp():
    execute(['scrapy', 'crawl', 'vetp'])


if __name__ == '__main__':
    # electro_torgi()
    uralbidin()
    # vetp()
