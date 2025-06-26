from scrapy.cmdline import execute


def rad():
    execute(["scrapy", "crawl", "rad", "-a"])


def confiscate():
    execute(["scrapy", "crawl", "confiscate"])


def lease():
    execute(["scrapy", "crawl", "lease"])


def privatization():
    execute(["scrapy", "crawl", "privatization"])


def arrested():
    execute(["scrapy", "crawl", "arrested"])


if __name__ == "__main__":
    rad()
