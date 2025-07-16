from scrapy.cmdline import execute


def sibtoptrade_bankruptcy():
    execute(["scrapy", "crawl", "sibtoptrade_bankruptcy"])


def sibtoptrade_commercial():
    execute(["scrapy", "crawl", "sibtoptrade_commercial"])

if __name__ == '__main__':
    sibtoptrade_commercial()
