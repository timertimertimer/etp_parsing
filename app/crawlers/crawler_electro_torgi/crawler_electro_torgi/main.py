from scrapy.cmdline import execute


def electro_torgi():
    execute(["scrapy", "crawl", "electro_torgi"])


def uralbidin():
    execute(["scrapy", "crawl", "uralbidin"])


def vetp_bankrupt():
    execute(["scrapy", "crawl", "vetp_bankrupt"])

def vetp_arrest():
    execute(["scrapy", "crawl", "vetp_arrest"])

if __name__ == "__main__":
    # electro_torgi()
    # uralbidin()
    # vetp_bankrupt()
    vetp_arrest()
