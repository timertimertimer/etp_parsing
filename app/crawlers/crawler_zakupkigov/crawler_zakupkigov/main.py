from scrapy.cmdline import execute


def zakupkigov_fz44():
    execute(["scrapy", "crawl", "zakupkigov_fz44"])


def zakupkigov_capital_repair():
    execute(["scrapy", "crawl", "zakupkigov_capital_repair"])


if __name__ == "__main__":
    zakupkigov_capital_repair()
