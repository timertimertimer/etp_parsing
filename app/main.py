import hashlib
import hmac
import os
import time
import requests
from random import choices
from string import ascii_letters, digits
from dotenv import load_dotenv
from concurrent.futures import ProcessPoolExecutor, as_completed

from db.models import AuctionPropertyType
from utils import logger
from utils.config import post_main_service

load_dotenv()
# set_logger(logger)  # FIXME


def run_spider(project: str, spider: str) -> None:
    logger.info(f"Started {project}/{spider}")
    start_spider_time = time.time()

    os.system(f"cd {project} && /usr/local/bin/scrapy crawl {spider}")

    spider_duration = time.time() - start_spider_time
    logger.info(f"Finished {project}/{spider} in {spider_duration:.2f} seconds")


def after_spiders():
    key_secret = os.getenv("PARSER_SECRET")
    url = os.getenv("SITE_URL")
    if not key_secret or not url:
        raise ValueError("PARSER_SECRET или SITE_URL не заданы в .env")
    url += "/api/parser/import"
    key = "".join(choices(ascii_letters + digits, k=32))
    signature = hmac.new(
        key_secret.encode("utf-8"), key.encode("utf-8"), hashlib.sha256
    ).hexdigest()
    headers = {"X-PARSER-KEY": key, "X-PARSER-SIGNATURE": signature}
    response = requests.post(url, headers=headers)
    logger.info(
        f"Status Code: {response.status_code}",
    )
    logger.info(f"Response: {response.text}")


itender = [
    "alfalot",
    "arbbitlot",
    "arbitat",
    "bepspb",
    "centerr_bankruptcy",
    "centerr_commercial",
    "etpu",
    "etpugra",
    "ets24_bankruptcy",
    "gloriaservice",
    "meta_invest",
    "propertytrade",
    "selt_online",
    "tender_one",
    "tendergarant",
    "torgibankrot",
    "utender",
    "utpl",
    "zakazrf",
]
altimeta = [
    "atctrade",
    "aukcioncenter",
    "ausib",
    "etp_profit",
    "ptp_center",
    "regtorg",
    "seltim",
]
electro_torgi = ["electro_torgi", "uralbidin", "vetp_bankrupt", "vetp_arrested"]
eurtp = ["eurtp_bankruptcy", "eurtp_arrested"]
ruson = [
    "eltorg_bankruptcy",
    "eltorg_commercial",
    "nistp",
    "promkonsalt",
    "ruson",
    "sistematorg",
]
sitesoft = [
    "cdtrf_arrested",
    "etpu_arrested",
    "etpu_commercial",
    "etpu_legal_entities",
    "alfalot_commercial",
    "tender_one_commercial"
]
tenderstandartru = ["au_pro", "tenderstandart", "torggroup", "viomitra"]
lot_online_catalog = [
    "lot_online_bankruptcy",
    "lot_online_private_property",
    "lot_online_rent",
]
lot_online_old = [
    "lot_online_old_rad",
    "lot_online_old_confiscate",
    "lot_online_old_lease",
    "lot_online_old_privatization",
    "lot_online_old_arrested",
]
zalog = ["lot_online_zalog_rshb", "lot_online_zalog_sbrf", "lot_online_zalog_rad"]

property_types = {AuctionPropertyType.bankruptcy: ["akosta"]}

crawlers = {
    "crawler_akosta": [
        f"akosta_{el}"
        for el in [
            AuctionPropertyType.bankruptcy,
            # AuctionPropertyType.arrested,
            # AuctionPropertyType.commercial
        ]
    ],
    "crawler_altimeta": altimeta,
    "crawler_b2b_center": "b2b_center_fz223",
    "crawler_bankrot_cdtrf": "bankrot_cdtrf",
    "crawler_ei": [
        f"ei_{el}"
        for el in [
            AuctionPropertyType.bankruptcy,
            AuctionPropertyType.arrested,
            AuctionPropertyType.commercial,
        ]
    ],
    "crawler_electro_torgi": electro_torgi,
    "crawler_ets24_arrested": "ets24_arrested",
    "crawler_eurtp": eurtp,
    "crawler_fabrikant": [
        f"fabrikant_{el}"
        for el in [
            AuctionPropertyType.bankruptcy,
            AuctionPropertyType.commercial,
            AuctionPropertyType.legal_entities,
            AuctionPropertyType.fz223,
        ]
    ],
    "crawler_heveya": [
        f"heveya_{el}"
        for el in [
            AuctionPropertyType.bankruptcy,
            AuctionPropertyType.arrested,
        ]
    ],
    "crawler_itender": itender,
    "crawler_kartoteka": "kartoteka",
    "crawler_lot_online_catalog": lot_online_catalog,
    "crawler_lot_online_old": lot_online_old,
    "crawler_lot_online_tender": "lot_online_tender",
    "crawler_lot_online_zalog": zalog,
    "crawler_mets": "mets",
    "crawler_moi_tender": "moi_tender",
    "crawler_opentp": "opentp",
    "crawler_roseltorg": [
        f"roseltorg_{el}"
        for el in [
            AuctionPropertyType.legal_entities,
            AuctionPropertyType.capital_repair,
            AuctionPropertyType.fz223,
        ]
    ],
    "crawler_rusonru": ruson,
    "crawler_rutrade24": [f"rutrade24_{el}" for el in [
        AuctionPropertyType.bankruptcy,
        AuctionPropertyType.commercial
    ]],
    "crawler_sberbank": [f"sberbank_{el}" for el in [
        AuctionPropertyType.bankruptcy,
        AuctionPropertyType.fz223,
        AuctionPropertyType.fz44,
        AuctionPropertyType.capital_repair,
        AuctionPropertyType.legal_entities,
        AuctionPropertyType.commercial
    ]],
    "crawler_sibtoptrade": [f"sibtoptrade_{el}" for el in [
        AuctionPropertyType.bankruptcy,
        AuctionPropertyType.commercial,
    ]],
    "crawler_sitesoft": sitesoft,
    "crawler_tenderstandartru": tenderstandartru,
    "crawler_torgidv": [f"torgidv_{el}" for el in [
        AuctionPropertyType.bankruptcy,
        AuctionPropertyType.arrested,
    ]],
    "crawler_torgigov": "torgigov",
    "crawler_vertrades": "vertrades",
    "crawler_zakupkigov": [f"zakupkigov_{el}" for el in [
        AuctionPropertyType.fz44,
        AuctionPropertyType.capital_repair,
    ]],
}


def main():
    start_time = time.time()
    logger.info("~~~~~ Started main ~~~~~")

    max_workers = 30
    futures = []

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        for crawler, spider in crawlers.items():
            if isinstance(spider, list):
                for sp in spider:
                    futures.append(executor.submit(run_spider, crawler, sp))
            else:
                futures.append(executor.submit(run_spider, crawler, spider))

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                logger.error(f"Ошибка при выполнении парсера: {e}")

    duration = time.time() - start_time
    logger.info(f"~~~~~ Finished main in {duration:.2f} seconds ~~~~~")

    if post_main_service:
        after_spiders()


if __name__ == "__main__":
    main()
