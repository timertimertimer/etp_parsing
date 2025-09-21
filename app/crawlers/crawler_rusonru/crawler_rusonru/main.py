from scrapy.cmdline import execute



def eltorg_bankruptcy():
    execute(["scrapy", "crawl", "eltorg_bankruptcy"])


def eltorg_commercial():
    execute(["scrapy", "crawl", "eltorg_commercial"])


def nistp():
    execute(["scrapy", "crawl", "nistp"])


def promkonsalt():
    execute(["scrapy", "crawl", "promkonsalt"])

def ruson():
    execute(["scrapy", "crawl", "ruson"])


def sistematorg():
    execute(["scrapy", "crawl", "sistematorg"])


if __name__ == "__main__":
    sistematorg()
