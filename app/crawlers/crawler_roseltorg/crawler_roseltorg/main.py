from scrapy.cmdline import execute


def roseltorg_legal_entities():
    execute(["scrapy", "crawl", "roseltorg_legal_entities"])


def roseltorg_capital_repair():
    execute(["scrapy", "crawl", "roseltorg_capital_repair"])


def roseltorg_fz223():
    execute(["scrapy", "crawl", "roseltorg_fz223"])


if __name__ == "__main__":
    roseltorg_fz223()
