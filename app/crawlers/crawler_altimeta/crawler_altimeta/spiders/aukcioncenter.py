from scrapy import Request

from app.utils import URL
from app.utils.config import write_log_to_file
from .base import AltimetaBaseSpider
from ..manage_spiders.combo import Combo
from ..config import stop_page


class AukcioncenterSpider(AltimetaBaseSpider):
    name = "aukcioncenter"
    custom_settings = {
        "LOG_FILE": f"{name}.log" if write_log_to_file else None,
    }

    def parse_serp(self, response, current_page):
        combo = Combo(response_=response)
        if links := combo.serp.get_trading_number_from_serp_page():
            for link, trading_number in links:
                url = URL.unquote_url(
                    self.start_url[0].replace("/index.html", "").strip()
                )
                url = URL.url_join(url, link)
                if url not in self.previous_trades:
                    yield Request(
                        url,
                        callback=self.parse_trade_page,
                        dont_filter=True,
                        cb_kwargs={"trading_number": trading_number},
                    )
        next_page = combo.serp.get_one_next_link()
        if next_page:
            current_page += 1
            if current_page <= stop_page:
                url = response.urljoin(next_page)
                yield Request(
                    url,
                    self.parse_serp,
                    dont_filter=True,
                    cb_kwargs={"current_page": current_page},
                )
