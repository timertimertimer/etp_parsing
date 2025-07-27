from scrapy.cmdline import execute


def cdtrf_arrested():
    execute(["scrapy", "crawl", "cdtrf_arrested"])


def etpu_arrested():
    execute(["scrapy", "crawl", "etpu_arrested"])


def alfalot_commercial():
    execute(["scrapy", "crawl", "alfalot_commercial"])


def etpu_commercial():
    execute(["scrapy", "crawl", "etpu_commercial"])


def tender_one_commercial():
    execute(["scrapy", "crawl", "tender_one_commercial"])


def etpu_legal_entities():
    execute(["scrapy", "crawl", "etpu_legal_entities"])


if __name__ == "__main__":
    etpu_legal_entities()
