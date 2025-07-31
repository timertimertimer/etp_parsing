from scrapy.cmdline import execute


def rutrade24_bankruptcy():
    execute(["scrapy", "crawl", "rutrade24_bankruptcy"])


def rutrade24_commercial():
    execute(["scrapy", "crawl", "rutrade24_commercial"])


if __name__ == "__main__":
    rutrade24_commercial()
