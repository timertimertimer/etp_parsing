from scrapy.cmdline import execute


def rshb():
    execute(["scrapy", "crawl", "lot_online_zalog_rshb"])


def sbrf():
    execute(["scrapy", "crawl", "lot_online_zalog_sbrf"])


def rad():
    execute(["scrapy", "crawl", "lot_online_zalog_rad"])


if __name__ == "__main__":
    rad()
