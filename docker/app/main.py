import hashlib
import hmac
import os
import time
import logging
import requests
from random import choices
from string import ascii_letters, digits
from multiprocessing import Process
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor, as_completed

from general_utils.work_with_text_and_number import set_logger
from general_utils.config import post_main_service

load_dotenv()
logger = logging.getLogger(__name__)
set_logger(logger)


def run_spider(project: str, spider: str) -> None:
    logger.info(f"Started {project}/{spider}")
    start_spider_time = time.time()

    os.system(f"cd {project} && /usr/local/bin/scrapy crawl {spider}")

    spider_duration = time.time() - start_spider_time
    logger.info(f"Finished {project}/{spider} in {spider_duration:.2f} seconds")


def after_spiders():
    key_secret = os.getenv("PARSER_SECRET")
    url = os.getenv("MAIN_SERVICE_URL")
    if not key_secret or not url:
        raise ValueError("PARSER_SECRET или MAIN_SERVICE_URL не заданы в .env")
    url += "/api/parser/import"
    key = ''.join(choices(ascii_letters + digits, k=32))
    signature = hmac.new(key_secret.encode('utf-8'), key.encode('utf-8'), hashlib.sha256).hexdigest()
    headers = {
        "X-PARSER-KEY": key,
        "X-PARSER-SIGNATURE": signature
    }
    response = requests.post(url, headers=headers)
    print("Status Code:", response.status_code)
    print("Response:", response.text)


itender = [
    'alfalot', 'arbbitlot', 'arbitat', 'bepspb', 'centerr', 'etpu', 'etpugra', 'ets24', 'gloriaservice', 'meta_invest',
    'propertytrade', 'selt_online', 'tender_one', 'tendergarant', 'torgibankrot', 'utender', 'utpl', 'zakazrf'
]
altimeta = ['atctrade', 'aukcioncenter', 'ausib', 'etp_profit', 'ptp_center', 'regtorg', 'seltim']
electro_torgi = ['electro_torgi', 'uralbidin', 'vetp']
ruson = ['eltorg', 'nistp', 'promkonsalt', 'ruson', 'sistematorg']
tenderstandartru = ['au_pro', 'tenderstandart', 'torggroup', 'viomitra']
lot_online_catalog = ['lot_online_bankruptcy', 'lot_online_private_property']
lot_online = ['rad', 'confiscate', 'lease', 'privatization', 'arrested']
zalog = ['rshb', 'sbrf', 'rad']

projects = {
    'crawler_akosta': 'akosta',
    'crawler_altimeta': altimeta,
    'crawler_bankrot_cdtrf': 'bankrot_cdtrf',
    'crawler_electro_torgi': electro_torgi,
    'crawler_eurtp': 'eurtp',
    'crawler_fabricant': 'fabrikant',
    'crawler_heveya': 'heveya',
    'crawler_itender': itender,
    'crawler_kartoteka': 'kartoteka',
    'crawler_lot_online_catalog': lot_online_catalog,
    'crawler_lot_online_old': lot_online,
    'crawler_lot_online_zalog': zalog,
    'crawler_mets': 'mets',
    'crawler_moi_tender': 'moi_tender',
    'crawler_opentp': 'opentp',
    # 'crawler_roseltorg': 'roseltorg',
    'crawler_rusonru': ruson,
    'crawler_rutrade24': 'rutrade24',
    'crawler_sberbank': 'sberbank',
    'crawler_sibtoptrade': 'sibtoptrade',
    'crawler_tenderstandartru': tenderstandartru,
    'crawler_torgidv': 'torgidv',
    'crawler_torgigov': 'torgigov',
    'crawler_vertrades': 'vertrades',
}


def main():
    start_time = time.time()
    logger.info(f"~~~~~ Started main ~~~~~")

    max_workers = 30
    futures = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for project, spider in projects.items():
            if isinstance(spider, list):
                for sp in spider:
                    futures.append(executor.submit(run_spider, project, sp))
            else:
                futures.append(executor.submit(run_spider, project, spider))

        # Ожидание завершения всех процессов
        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Ошибка при выполнении парсера: {e}")

    duration = time.time() - start_time
    logger.info(f"~~~~~ Finished main in {duration:.2f} seconds ~~~~~")

    if post_main_service:
        after_spiders()

if __name__ == '__main__':
    main()
