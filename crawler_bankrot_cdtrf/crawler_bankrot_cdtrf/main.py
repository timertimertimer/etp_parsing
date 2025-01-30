from scrapy.cmdline import execute


def bankrot_cd_auction():
    execute(['scrapy', 'crawl', 'bankrot_cd_auction'])


def bankrot_cd_competition():
    execute(['scrapy', 'crawl', 'bankrot_cd_competition'])


def bankrot_cd_offer():
    execute(['scrapy', 'crawl', 'bankrot_cd_offer'])


if __name__ == '__main__':
    bankrot_cd_offer()
