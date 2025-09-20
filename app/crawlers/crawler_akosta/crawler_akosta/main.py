from scrapy.cmdline import execute


def akosta_bankruptcy():
    execute(["scrapy", "crawl", "akosta_bankruptcy"])


def akosta_arrested():  # FIXME: иногда попадает в банкротство
    execute(["scrapy", "crawl", "akosta_arrested"])


def akosta_commercial():  # FIXME: иногда попадает в банкротство
    execute(["scrapy", "crawl", "akosta_commercial"])


if __name__ == "__main__":
    akosta_bankruptcy()
