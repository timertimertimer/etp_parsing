import os
import logging
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


def run_spider(project: str, spider: str) -> None:
    os.system(f"cd {project} && scrapy crawl {spider}")


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
            logger.info(f'Starting {project}/{sp}')
            p = Process(target=run_spider, args=(project, sp))
            p.start()
            processes.append(p)
    else:
        logger.info(f'Starting {project}/{spider}')
        p = Process(target=run_spider, args=(project, spider))
        p.start()
        processes.append(p)

for p in processes:
    p.join()
