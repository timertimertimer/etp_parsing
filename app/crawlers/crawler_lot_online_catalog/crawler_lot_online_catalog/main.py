from scrapy.cmdline import execute


def bankruptcy():
    execute(["scrapy", "crawl", "lot_online_bankruptcy"])


def private_property():
    execute(["scrapy", "crawl", "lot_online_private_property"])


def lot_online_rent():
    execute(["scrapy", "crawl", "lot_online_rent"])


if __name__ == "__main__":
    lot_online_rent()
