from scrapy.cmdline import execute


def heveya_bankruptcy():
    execute(["scrapy", "crawl", "heveya_bankruptcy"])


def heveya_arrested():
    execute(["scrapy", "crawl", "heveya_arrested"])


if __name__ == "__main__":
    # heveya_bankruptcy()
    heveya_arrested()
