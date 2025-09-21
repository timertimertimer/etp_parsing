from scrapy.cmdline import execute


def ei_bankruptcy():
    execute(["scrapy", "crawl", "ei_bankruptcy"])


def ei_arrested():
    execute(["scrapy", "crawl", "ei_arrested"])


def ei_commercial():
    execute(["scrapy", "crawl", "ei_commercial"])


if __name__ == "__main__":
    ei_commercial()
