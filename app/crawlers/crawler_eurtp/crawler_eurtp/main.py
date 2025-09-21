from scrapy.cmdline import execute


def eurtp_bankruptcy():
    execute(["scrapy", "crawl", "eurtp_bankruptcy"])


def eurtp_arrested():
    execute(["scrapy", "crawl", "eurtp_arrested"])


if __name__ == "__main__":
    eurtp_bankruptcy()
    # eurtp_arrested()
