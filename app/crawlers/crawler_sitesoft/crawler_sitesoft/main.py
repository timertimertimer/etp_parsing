from scrapy.cmdline import execute


def cdtrf_arrested():
    execute(["scrapy", "crawl", "cdtrf_arrested"])


def etpu_arrested():
    execute(["scrapy", "crawl", "etpu_arrested"])


def alfalot_commercial():
    execute(["scrapy", "crawl", "alfalot_commercial"])


if __name__ == "__main__":
    alfalot_commercial()
