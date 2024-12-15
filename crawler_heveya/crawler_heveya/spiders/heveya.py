import scrapy
from scrapy import Request, FormRequest

from ..app import Combo
from ..utils.get_data_from_table import DbConnectCheckLots
from ..utils.config import params, data_origin_url
from ..items import CrawlerHeveyaItem, CrawlerHeveyaItemLoader
from ..utils.working_with_time import return_parse_date


class HeveyaSpider(scrapy.Spider):
    name = "heveya"
    start_urls = ["https://heveya.ru/search"]

    def __init__(self):
        super(HeveyaSpider, self).__init__()
        self.db_check = DbConnectCheckLots()
        self.previous_lots = self.db_check.get_latest_lot()
        
    def start_requests(self):
        yield FormRequest(self.start_urls[0], self.parse_serp, formdata=params, method='GET')

    def parse_serp(self, response):
        combo = Combo(response)
        for lot in combo.soup.find_all('div', class_='lot'):
            link = lot.find('a').get('href')
            if link not in self.previous_lots:
                status = combo.soup.find('div', class_='noBids')
                if status:
                    status = 'pending' if 'noBids_theme_blue' in status.get('class') else 'ended'
                else:
                    status = 'active'
                yield Request(link, self.parse_lot, cb_kwargs={'status': status})
        next_page = combo.soup.find('a', {'aria-label': 'pagination.next'})
        if next_page:
            yield FormRequest(next_page['href'], self.parse_serp, method='GET')
                
    def parse_lot(self, response, status):
        combo = Combo(response)
        loader = CrawlerHeveyaItemLoader(CrawlerHeveyaItem(), response=response)
        trading_type, trading_org, trading_org_contacts, start_price, step_price = combo.get_main_info()
        loader.add_value("data_origin", data_origin_url)
        loader.add_value("trading_id", combo.trading_id)
        loader.add_value("trading_link", response.url)
        loader.add_value("trading_number", combo.trading_number)
        loader.add_value("trading_type", trading_type)
        loader.add_value("trading_form", combo.trading_form)
        loader.add_value("trading_org", trading_org)
        loader.add_value("trading_org_contacts", trading_org_contacts)
        loader.add_value("case_number", combo.case_number)
        loader.add_value("debtor_inn", combo.debtor_inn)
        loader.add_value("arbit_manager", combo.arbit_manager)
        loader.add_value("arbit_manager_inn", combo.arbit_manager_inn)
        loader.add_value("arbit_manager_org", combo.arbit_manager_org)
        loader.add_value("status", status)
        loader.add_value("lot_id", combo.lot_id)
        loader.add_value("lot_link", combo.lot_link)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_date_requests", combo.start_date_requests)
        loader.add_value("end_date_requests", combo.end_date_requests)
        loader.add_value("start_date_trading", combo.start_date_trading)
        loader.add_value("end_date_trading", combo.end_date_trading)
        loader.add_value("start_price", combo.start_price)
        loader.add_value("step_price", combo.step_price)
        loader.add_value("periods", combo.periods)
        loader.add_value("files", {"general": combo.download_general(), "lot": combo.download_lot()})
        loader.add_value("created_at", return_parse_date())
        yield loader.load_item()
        
