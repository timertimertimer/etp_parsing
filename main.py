import os
import logging
import time
from multiprocessing import Process

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

if not logger.hasHandlers():
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

start_time = time.time()
logger.info(f"~~~~~ Started main ~~~~~")


def run_spider(project: str, spider: str) -> None:
    logger.info(f"Started {project}/{spider}")
    start_spider_time = time.time()

    os.system(f"cd {project} && scrapy crawl {spider}")

    spider_duration = time.time() - start_spider_time
    logger.info(f"Finished {project}/{spider} in {spider_duration:.2f} seconds")


itender = [
    'alfalot', 'arbbitlot', 'arbitat', 'bepspb', 'centerr', 'etpu', 'etpugra', 'ets24', 'gloriaservice', 'meta_invest',
    'propertytrade', 'selt_online', 'tender_one', 'tendergarant', 'torgibankrot', 'utender', 'utpl', 'zakazrf'
]

projects = {
    'crawler_akosta': 'akosta',
    'crawler_itender': itender
}

processes = []
for project, spider in projects.items():
    if isinstance(spider, list):
        for sp in spider:
            p = Process(target=run_spider, args=(project, sp))
            p.start()
            processes.append((p, project, sp))
    else:
        p = Process(target=run_spider, args=(project, spider))
        p.start()
        processes.append((p, project, spider))

for p, project, spider in processes:
    start_time = time.time()
    p.join()
    duration = time.time() - start_time
duration = time.time() - start_time
logger.info(f"~~~~~ Finished main in {duration:.2f} seconds ~~~~~")
