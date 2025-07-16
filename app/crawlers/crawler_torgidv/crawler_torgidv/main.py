from scrapy.cmdline import execute


def torgidv_arrested():
    execute(["scrapy", "crawl", "torgidv_arrested"])


def torgidv_bankruptcy():
    execute(["scrapy", "crawl", "torgidv_bankruptcy"])


if __name__ == "__main__":
    # torgidv_bankruptcy()
    torgidv_arrested()
