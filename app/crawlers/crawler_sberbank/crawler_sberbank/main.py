from scrapy.cmdline import execute


def sberbank_bankruptcy():
    execute(["scrapy", "crawl", "sberbank_bankruptcy"])


def sberbank_fz223():
    execute(["scrapy", "crawl", "sberbank_fz223"])


def sberbank_fz44():
    execute(["scrapy", "crawl", "sberbank_fz44"])


def sberbank_capital_repair():
    execute(["scrapy", "crawl", "sberbank_capital_repair"])


def sberbank_legal_entities():
    execute(["scrapy", "crawl", "sberbank_legal_entities"])


def sberbank_commercial():
    execute(["scrapy", "crawl", "sberbank_commercial"])


if __name__ == '__main__':
    # sberbank_bankruptcy()
    # sberbank_fz223()
    # sberbank_fz44()
    # sberbank_capital_repair()
    # sberbank_legal_entities()
    sberbank_commercial()
