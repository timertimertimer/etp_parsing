from scrapy.cmdline import execute


def b2b_fz223():
    execute(['scrapy', 'crawl', 'b2b_center_fz223'])


if __name__ == '__main__':
    b2b_fz223()
