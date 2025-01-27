from urllib.parse import urlparse, parse_qs, urlencode
url_pagination ='https://sistematorg.com/tradelist.php?trade_number=&debtor_info=&arbitr_info=&app_start_from' \
                '=&app_start_to=&app_end_from=&app_end_to=&trade_type=%D0%9B%D1%8E%D0%B1%D0%BE%D0%B9&trade_state=%D0' \
                '%9B%D1%8E%D0%B1%D0%BE%D0%B9&pagenum={}'


def parse_new_url(url, page_number):
    url_parsed = urlparse(url)
    print(url_parsed)
parse_new_url(url_pagination, 2)
