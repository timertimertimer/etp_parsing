import os
from multiprocessing import Process


def run_spider(project, spider):
    os.system(f"cd {project} && scrapy crawl {spider}")


itender = [
    'alfalot', 'arbbitlot', 'arbitat', 'bepspb', 'centerr', 'etpu', 'etpugra', 'ets24', 'gloriaservice', 'meta_invest',
    'propertytrade', 'selt_online', 'tender_one', 'tendergarant', 'torgibankrot', 'utender', 'utpl', 'zakazrf'
]

projects = {
               'crawler_akosta': 'akosta'
           } | {
               'crawler_itender': project for project in itender
           }

processes = []
for project, spider in projects.items():
    p = Process(target=run_spider, args=(project, spider))
    p.start()
    processes.append(p)

for p in processes:
    p.join()
