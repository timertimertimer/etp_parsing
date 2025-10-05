import scrapy

from app.crawlers.items import EtpItem, EtpItemLoader
from app.db.models import AuctionPropertyType
from app.utils import URL
from app.crawlers.base import BaseSpider
from app.utils.config import start_date, end_date, write_log_to_file
from ..combo import Combo
from ..config import bankrupt_categories, arrested_categories, page_limit
from ..config import data_origin_url


class EurtpBaseSpider(BaseSpider):
    start_urls = ["http://eurtp.ru/"]
    category_urls = []

    def __init__(self):
        super().__init__(data_origin_url)

    def parse(self, response, **kwargs):
        for category in self.category_urls:
            yield scrapy.FormRequest(
                url=category,
                method="POST",
                formdata={"page": "1", "DateStart": start_date, "DateFinish": end_date},
                callback=self.collect_links,
            )

    def collect_links(self, response, current_page: int = 1, all_links: set = None):
        links_on_page = {
            tr.css("td:nth-child(2)>a::attr(href)").get()
            for tr in response.css(".table-responsive table:nth-child(2) tr")[1:]
        }
        all_links = all_links or set()
        all_links.update(links_on_page)
        pages = response.xpath('//div[@class="pager"]/a')
        if pages:
            next_page = pages[-2]
            next_page_number = int(next_page.xpath("./@data-page").get())
            if next_page_number <= page_limit:
                next_page_url = next_page.xpath("./@href").get()
                if next_page_number > current_page:
                    current_page = next_page_number
                    yield scrapy.Request(
                        url=URL.url_join(data_origin_url, next_page_url),
                        cb_kwargs=dict(current_page=current_page, all_links=all_links),
                        callback=self.collect_links,
                    )
                    return
        for link in all_links:
            link = URL.url_join(data_origin_url, link)
            if link not in self.previous_trades:
                yield scrapy.Request(url=link, callback=self.parse_trades)

    def parse_trades(self, response):
        combo = Combo(response)
        lots_on_page = [
            tr.css("td:nth-child(2)>a::attr(href)").get()
            for tr in response.css(
                ".table-responsive:first-child table:nth-child(2) tr"
            )[1:]
        ]
        trading_id = combo.trading_id
        trading_link = combo.trading_link
        trading_number = combo.trading_number
        trading_type = combo.trading_type
        trading_form = combo.trading_form
        trading_org = combo.trading_org
        trading_org_contacts = combo.trading_org_contacts
        case_number = combo.case_number
        debtor_inn = combo.debtor_inn
        address = combo.address
        arbit_manager = combo.arbit_manager
        arbit_manager_inn = combo.arbit_manager_inn
        arbit_manager_org = combo.arbit_manager_org
        general_files = combo.download()
        for lot_link in lots_on_page:
            loader = EtpItemLoader(item=EtpItem(), response=response)
            loader.add_value("data_origin", data_origin_url)
            loader.add_value("property_type", self.property_type)
            loader.add_value("trading_id", trading_id)
            loader.add_value("trading_link", trading_link)
            loader.add_value("trading_number", trading_number)
            loader.add_value("trading_type", trading_type)
            loader.add_value("trading_form", trading_form)
            loader.add_value("trading_org", trading_org)
            loader.add_value("trading_org_contacts", trading_org_contacts)
            loader.add_value("case_number", case_number)
            loader.add_value("debtor_inn", debtor_inn)
            loader.add_value("address", address)
            loader.add_value("arbit_manager", arbit_manager)
            loader.add_value("arbit_manager_inn", arbit_manager_inn)
            loader.add_value("arbit_manager_org", arbit_manager_org)
            loader.add_value("start_date_requests", combo.start_date_requests)
            loader.add_value("end_date_requests", combo.end_date_requests)
            loader.add_value("start_date_trading", combo.start_date_trading)
            loader.add_value("categories", None)
            yield scrapy.Request(
                url=URL.url_join(data_origin_url, lot_link),
                callback=self.parse_lot,
                cb_kwargs={"loader": loader, "general_files": general_files},
            )

    def parse_lot(self, response, loader, general_files):
        combo = Combo(response)
        loader.add_value("lot_id", combo.lot_id)
        loader.add_value("lot_link", combo.lot_link)
        loader.add_value("lot_number", combo.lot_number)
        loader.add_value("short_name", combo.short_name)
        loader.add_value("lot_info", combo.lot_info)
        loader.add_value("property_information", combo.property_information)
        loader.add_value("start_price", combo.start_price)
        if loader.get_collected_values("trading_type")[0] in ["auction", "competition"]:
            loader.add_value("step_price", combo.step_price)
        else:
            loader.add_value("start_date_requests", combo.start_date_requests)
            loader.add_value("end_date_requests", combo.end_date_requests)
            loader.add_value("start_date_trading", combo.start_date_trading)
            loader.add_value("end_date_trading", combo.end_date_trading)
            loader.add_value("periods", combo.periods)
        loader.add_value("files", {"general": general_files, "lot": combo.download()})
        yield loader.load_item()


class EurtpBankruptcySpider(EurtpBaseSpider):
    name = "eurtp_bankruptcy"
    property_type = AuctionPropertyType.bankruptcy
    category_urls = bankrupt_categories
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }


class EurtpArrestedSpider(EurtpBaseSpider):
    name = "eurtp_arrested"
    property_type = AuctionPropertyType.arrested
    category_urls = arrested_categories
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }
