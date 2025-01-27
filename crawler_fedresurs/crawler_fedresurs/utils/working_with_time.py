from datetime import datetime


def return_parse_date():
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')
