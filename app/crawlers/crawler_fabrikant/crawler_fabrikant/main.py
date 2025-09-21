from scrapy.cmdline import execute


def bankruptcy():
    execute(["scrapy", "crawl", "fabrikant_bankruptcy"])


def commercial():
    execute(["scrapy", "crawl", "fabrikant_commercial"])


def legal_entities():
    execute(["scrapy", "crawl", "fabrikant_legal_entities"])


def fz223():
    execute(["scrapy", "crawl", "fabrikant_fz223"])


if __name__ == "__main__":
    # bankruptcy()
    # commercial()
    # legal_entities()
    fz223()
