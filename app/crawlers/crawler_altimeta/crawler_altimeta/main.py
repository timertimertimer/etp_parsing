from scrapy.cmdline import execute


def ausib():
    execute(["scrapy", "crawl", "ausib"])


def ptp_center():
    execute(["scrapy", "crawl", "ptp_center"])


def regtorg():
    execute(["scrapy", "crawl", "regtorg"])


def etp_profit():
    execute(["scrapy", "crawl", "etp_profit"])


def seltim():
    execute(["scrapy", "crawl", "seltim"])


def atctrade():
    execute(["scrapy", "crawl", "atctrade"])


def aukcioncenter():
    execute(["scrapy", "crawl", "aukcioncenter"])


if __name__ == "__main__":
    ausib()
