from scrapy import Request, FormRequest

from app.db.models import AuctionPropertyType
from app.utils import URL
from .base import RusonBaseSpider
from app.utils.config import write_log_to_file
from ..config import trade_link, formdata, serp_link
from ..trades.combo import Combo


class RusonSpider(RusonBaseSpider):
    name = "ruson"
    property_type = AuctionPropertyType.bankruptcy
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def parse_serp(self, response, all_links: set = None):
        combo = Combo(response=response)
        current_page = combo.serp.get_curent_page()
        next_page = combo.serp.get_next_page()
        links = combo.serp.links_to_trade(table_class="node_view")
        all_links = (all_links or set()).union(links)
        if next_page and current_page < next_page:
            formdata["pagenum"] = str(next_page)
            yield FormRequest(
                url="".join(serp_link[self.name]),
                callback=self.parse_serp,
                formdata=formdata,
                method="GET",
                errback=self.errback_httpbin,
                cb_kwargs={"all_links": all_links},
            )
        else:
            for link in all_links:
                link = URL.url_join(trade_link[self.name], link[0])
                if link not in self.previous_trades:
                    yield Request(url=link, callback=self.parse_trade)
