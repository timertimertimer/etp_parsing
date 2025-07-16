from app.utils.config import start_date

data_origin_url = 'http://ets24.ru/'
base_url = 'https://ets24.ru/index.php'
params = {
    'PresentStartDateMin': start_date,
    'IsSuspendedTrading': '0',
    'AuctionType': 'Arrest',
    'page': '1'
}