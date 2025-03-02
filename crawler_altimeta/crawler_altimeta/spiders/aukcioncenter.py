from scrapy import Request

from general_utils import UrlConfig
from .base import AltimetaBaseSpider
from ..manage_spiders.app import Combo
from ..utils.config import stop_page


class AukcioncenterSpider(AltimetaBaseSpider):
    name = 'aukcioncenter'

    def parse_serp(self, response, current_page):
        combo = Combo(response_=response)
        if links := combo.serp.get_trading_number_from_serp_page():
            for link, trading_number in links:
                url = UrlConfig.unquote_url(self.start_url[0].replace('/index.html', '').strip())
                url = UrlConfig.url_join(url, link)
                if url not in self.previous_lots:
                    yield Request(
                        url, callback=self.parse_trade_page, dont_filter=True,
                        cb_kwargs={'trading_number': trading_number}
                    )
        next_page = combo.serp.get_one_next_link()
        if next_page:
            current_page += 1
            if current_page <= stop_page:
                url = response.urljoin(next_page)
                yield Request(url, self.parse_serp, dont_filter=True, cb_kwargs={'current_page': current_page})
