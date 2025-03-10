import copy
import logging
from scrapy import Request
from general_utils.base_spider import BaseSpider
from ..manage_spiders.app import Combo
from ..utils.config import return_auction_link, data_origin, return_offer_link, return_compet_link

logger = logging.getLogger(__name__)


class ItenderBaseSpider(BaseSpider):
    name = 'base'
    custom_settings = {
        # 'LOG_FILE': f'{name}.log',
    }

    @classmethod
    def set_links(cls):
        cls.data_origin = data_origin.get(cls.name)

    def __init__(self):
        self.set_links()
        super(ItenderBaseSpider, self).__init__(self.data_origin)

    def start_requests(self):
        yield Request(self.data_origin, self.choose_datatype)

    def choose_datatype(self, response):
        for _type in ['auction', 'offer', 'competition']:
            if _type == 'auction':
                yield Request(return_auction_link(self.data_origin), self.parse_, cb_kwargs={'_type': 'auction'})
            if _type == 'offer':
                yield Request(return_offer_link(self.data_origin), self.parse_, cb_kwargs={'_type': 'offer'})
            if _type == 'competition':
                yield Request(return_compet_link(self.data_origin), self.parse_, cb_kwargs={'_type': 'competition'})

    def parse_(self, response, _type: str):
        first_post = None
        function_for_parse = None
        combo = Combo(response)
        if _type == 'auction':
            first_post = copy.deepcopy(pdac)
            function_for_parse = self.parse_serp_auction
            first_post[
                'ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_Датапроведенияс_dateInput'] = start_date
        if _type == 'offer':
            first_post = copy.deepcopy(pdao)
            function_for_parse = self.parse_serp_offer
            first_post[
                'ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_bidSubmissionStartDate_Датаначалапредставлениязаявокнаучастиес_dateInput'] = start_date
        if _type == 'competition':
            first_post = copy.deepcopy(pdcom)
            function_for_parse = self.parse_competiton_serp
            first_post[
                'ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_Датапроведенияс_dateInput'] = start_date
        first_post['__EVENTTARGET'] = combo.mpost.get_post_data_values(tag_html='input', post_argument='__EVENTTARGET')
        first_post['__EVENTARGUMENT'] = combo.mpost.get_post_data_values('input', '__EVENTARGUMENT')
        first_post['__CVIEWSTATE'] = combo.mpost.get_post_data_values('input', '__CVIEWSTATE')
        first_post['__VIEWSTATE'] = combo.mpost.get_post_data_values('input', '__VIEWSTATE')
        first_post['__EVENTVALIDATION'] = combo.mpost.get_post_data_values('input', '__EVENTVALIDATION')
        yield FormRequest(response.url, formdata=first_post, callback=function_for_parse,
                          cb_kwargs={'first_post': first_post})