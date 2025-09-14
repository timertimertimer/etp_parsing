from scrapy.cmdline import execute


def rad():
    execute(["scrapy", "crawl", "lot_online_old_rad"])


def confiscate():
    execute(["scrapy", "crawl", "lot_online_old_confiscate"])


def lease():
    execute(["scrapy", "crawl", "lot_online_old_lease"])


def privatization():
    execute(["scrapy", "crawl", "lot_online_old_privatization"])


def arrested():
    execute(["scrapy", "crawl", "lot_online_old_arrested"])


if __name__ == "__main__":
    arrested()
