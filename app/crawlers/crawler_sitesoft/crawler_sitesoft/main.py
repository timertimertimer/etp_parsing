from scrapy.cmdline import execute


def cdtrf_arrested():
    execute(["scrapy", "crawl", "cdtrf_arrested"])


if __name__ == "__main__":
    cdtrf_arrested()