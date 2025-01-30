import copy
import logging
from itertools import chain
from scrapy import Spider, Request, FormRequest
from general_utils.db import DBHelper
from general_utils.config import start_date
from general_utils.items import CrawlerBankruptItem, CrawlerBankruptItemLoader
from general_utils.working_with_time import return_servertime, return_parse_date
from ..manage_spider.app import Combo
from ..utils.config import search_link, data_origin, common_link, debtor_link, lot_link, _link_post_period
from ..utils.post_data import post_data_date_query, post_data_pagination, post_data_to_trade, \
    post_data_panel_list_query, post_data_debitor, post_data_lot_tab, post_data_unique_lot_page, \
    post_data_period_offer_page

logger = logging.getLogger(__name__)


class AkostaSpider(Spider):
    name = 'akosta'
    start_urls = ['https://www.akosta.info/akosta/lots.xhtml']
    custom_settings = {
        'UNIQUE_CO': ['trading_id', 'lot_number'],
        # 'LOG_FILE': f'{name}.log'
    }

    def __init__(self, *args, **kwargs):
        super(AkostaSpider, self).__init__(*args, **kwargs)
        self.db_check = DBHelper(self.custom_settings.get('TABLE_NAME', f'lots_{self.name}'))
        self.previous_lots = self.db_check.get_latest_lot(['trading_id'])

    def start_requests(self):
        yield Request(self.start_urls[0] + '?sgUnid=3', self.parse)

    def parse(self, response, **kwargs):
        combo = Combo(response)
        viewstate = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        post_data_date_query["formMain:inputServerTime"] = return_servertime()
        post_data_date_query["javax.faces.ViewState"] = viewstate
        post_data_date_query["formMain:fromIdAcceptancePeriod_input"] = start_date
        # post_data_date_query["formMain:toIdAcceptancePeriod_input"] = ''
        yield FormRequest(
            self.start_urls[0], callback=self.refresh_from_date, formdata=post_data_date_query, dont_filter=True
        )

    def refresh_from_date(self, response):
        yield Request(response.url, self.post_make_panel_list, dont_filter=True)

    def post_make_panel_list(self, response):
        combo = Combo(response)
        viewstate = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        post_data_panel_list_query["formMain:inputServerTime"] = return_servertime()
        post_data_panel_list_query["javax.faces.ViewState"] = viewstate
        post_data_panel_list_query["formMain:fromIdAcceptancePeriod_input"] = start_date
        # post_data_panel_list_query["formMain:toIdAcceptancePeriod_input"] = ''
        yield FormRequest.from_response(
            response, callback=self.refresh_panel_list, formdata=post_data_panel_list_query, dont_filter=True
        )

    def refresh_panel_list(self, response):
        yield Request(
            response.url, self.parse_panel_list, cb_kwargs={'page_number': 1, 'total_pages': 0, 'viewstate': None},
            dont_filter=True
        )

    def parse_panel_list(self, response, page_number, total_pages, viewstate):
        combo = Combo(response)
        if page_number == 1:
            current_page, total_pages = combo.pre.get_total_and_current_page
            sources = dict()
            for tag_tr in combo.pre.get_trade_links():
                data, id_ = combo.pre.get_post_id_and_trading_id(tag_tr)
                if (id_, ) in self.previous_lots:
                    continue
                if id_ not in sources:
                    sources[id_] = data
        else:
            sources = combo.pre.get_trade_links_2()
        if sources:
            yield from self.process_trade_one_by_one(response, sources, page_number, total_pages, viewstate)

    def process_trade_one_by_one(self, response, sources, page_number, total_pages, viewstate):
        combo = Combo(response)
        viewstate = viewstate or combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        if sources:
            id_, data = sources.popitem()
            post_data = copy.deepcopy(post_data_to_trade)
            post_data['javax.faces.source'] = data
            post_data["formMain:inputServerTime"] = return_servertime()
            post_data["formMain:fromIdAcceptancePeriod_input"] = start_date
            post_data["javax.faces.ViewState"] = viewstate
            post_data[data] = data
            yield FormRequest(
                search_link, self.redirect_trade_page, formdata=post_data, dont_filter=True,
                cb_kwargs={
                    "sources": sources,
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "trading_id": id_
                }
            )
        else:
            if page_number < total_pages:
                page_number += 1
                data_lots = int(page_number) * 50 - 50
                post_data_pagination["formMain:lotListTable_first"] = str(data_lots)
                post_data_pagination["formMain:inputServerTime"] = return_servertime()
                post_data_pagination["javax.faces.ViewState"] = viewstate
                yield FormRequest.from_response(
                    response, callback=self.parse_panel_list, formdata=post_data_pagination, dont_filter=True,
                    cb_kwargs={'page_number': page_number, 'total_pages': total_pages, 'viewstate': viewstate}
                )

    def redirect_trade_page(self, response, trading_id, sources, page_number, total_pages):
        combo = Combo(_response=response)
        url_to_trade = combo.main_.get_link_redirect()
        if url_to_trade:
            yield Request(
                url_to_trade, self.parse_trade_page, dont_filter=True, cb_kwargs={
                    "sources": sources,
                    "page_number": page_number,
                    "total_pages": total_pages,
                    "trading_id": trading_id
                }
            )

    def parse_trade_page(self, response, sources, page_number, total_pages, trading_id):
        combo = Combo(_response=response)
        transfer = CrawlerBankruptItem()
        transfer['data_origin'] = data_origin
        transfer['trading_id'] = trading_id
        transfer['trading_link'] = response.url
        trading_type = combo.trade.get_trading_type()
        transfer['trading_type'] = trading_type
        transfer['trading_form'] = combo.trade.get_trading_form()
        transfer['trading_org'] = combo.trade.get_org_name()
        transfer['trading_org_contacts'] = combo.trade.get_org_contacts()
        if trading_type in ('auction', 'competition'):
            transfer['start_date_requests'] = combo.main_.start_date_req_auc()
            transfer['end_date_requests'] = combo.main_.end_date_request_auc()
            transfer['start_date_trading'] = combo.main_.start_date_trading_auc()
            transfer['end_date_trading'] = combo.main_.end_date_trading_auc()

        # !!! DOCS !!!
        new_view = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        general_files = combo.main_.download_trade(
            url=common_link, trading_id=''.join(transfer['trading_id']), view=new_view,
            cookies=response.request.headers['Cookie'].decode()
        )

        post_data = copy.deepcopy(post_data_debitor)
        post_data['formMain:inputServerTime'] = return_servertime()
        post_data['javax.faces.ViewState'] = new_view
        for form_number_search in combo.deb.find_correct_form_number_collapsed():
            post_data[form_number_search] = 'false'
        form_number = combo.deb.find_correct_form_number()
        post_data[form_number] = form_number
        yield FormRequest(
            common_link, callback=self.parse_debitor, dont_filter=True, formdata=post_data,
            cb_kwargs={
                'transfer': transfer, 'trading_type': trading_type, 'files': general_files,
                'sources': sources, 'page_number': page_number, 'total_pages': total_pages
            }
        )

    def parse_debitor(self, response, transfer, trading_type, files, sources, page_number, total_pages):
        """ parse debtor tab(page), get new viewstate  and make requests to lot tab(page) """
        combo = Combo(_response=response)
        debtor_view_state = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        transfer['trading_number'] = combo.deb.get_trading_number()
        transfer['msg_number'] = combo.deb.get_msg_number()
        transfer['case_number'] = combo.deb.get_case_number()
        transfer['arbit_manager_inn'] = combo.deb.get_arbitr_inn()
        transfer['arbit_manager'] = combo.deb.get_arbitr_full_name()
        transfer['arbit_manager_org'] = combo.deb.get_arbitr_company()
        transfer['debtor_inn'] = combo.deb.get_debtor_inn()
        if combo.deb.soup.find('input', type='checkbox')['checked']:
            transfer['trading_org_inn'] = transfer['arbit_manager_inn']
        transfer['address'], transfer['region'] = combo.deb.get_debtor_address() or (None, None)
        post_data_lot_tab['formMain:inputServerTime'] = return_servertime()
        post_data_lot_tab['javax.faces.ViewState'] = debtor_view_state
        yield FormRequest(
            debtor_link, callback=self.parse_lot_tab, formdata=post_data_lot_tab, dont_filter=True,
            cb_kwargs={
                'transfer': transfer, 'trading_type': trading_type, 'files': files, 'lots': None,
                'sources': sources, 'page_number': page_number, 'total_pages': total_pages
            },
        )

    def parse_lot_tab(self, response, transfer, trading_type, files, lots, sources, page_number,
                      total_pages, current_lot=None):
        """ fetch post data to all unique lot and make post request """
        combo = Combo(_response=response)
        lot_tab_link = response.url
        if not current_lot:
            lots = lots if lots else combo.trade.get_post_lot_data()
            current_lot = lots.pop(0)
        post_lot = copy.deepcopy(post_data_unique_lot_page)
        post_lot['javax.faces.source'] = current_lot
        post_lot[current_lot] = current_lot
        post_lot['formMain:inputServerTime'] = return_servertime()
        viewstate = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
        post_lot['javax.faces.ViewState'] = viewstate
        lot_number = combo.trade.get_lot_number(_id=current_lot)
        yield FormRequest(
            lot_link, callback=self.parse_pre_lot_page, formdata=post_lot, dont_filter=True,
            cb_kwargs={
                'files': files, 'trading_type': trading_type, 'transfer': transfer, 'lot_number': lot_number,
                'sources': sources, 'page_number': page_number, 'total_pages': total_pages, 'lots': lots,
                'current_lot': current_lot, 'lot_tab_link': lot_tab_link
            }
        )
        if len(lots) > 0:
            yield Request(
                lot_tab_link, callback=self.parse_lot_tab, cb_kwargs={
                    'transfer': transfer,
                    'trading_type': trading_type,
                    'files': files,
                    'lots': lots,
                    'sources': sources, 'page_number': page_number, 'total_pages': total_pages
                },
                dont_filter=True
            )
        else:
            yield Request(
                search_link, self.process_trade_one_by_one, dont_filter=True,
                cb_kwargs={
                    'sources': sources,
                    'page_number': page_number,
                    'total_pages': total_pages,
                    'viewstate': None
                }
            )

    def parse_pre_lot_page(self, response, transfer, trading_type, files, lot_number, sources, page_number,
                           total_pages, lots, current_lot, lot_tab_link):
        """ get link to lot """
        combo = Combo(_response=response)
        url_to_trade = combo.main_.get_link_redirect()
        if url_to_trade:
            if trading_type == 'offer':
                yield Request(
                    url_to_trade, callback=self.parse_lot_offer, dont_filter=True, cb_kwargs={
                        'transfer': transfer, 'url_to_trade': url_to_trade, 'lot_number': lot_number, 'files': files,
                        'sources': sources, 'page_number': page_number, 'total_pages': total_pages
                    }
                )
            if trading_type == 'auction':
                yield Request(
                    url_to_trade, callback=self.parse_lot_auction, dont_filter=True, cb_kwargs={
                        'transfer': transfer, 'url_to_trade': url_to_trade, 'lot_number': lot_number, 'files': files,
                        'sources': sources, 'page_number': page_number, 'total_pages': total_pages
                    }
                )

            if trading_type == 'competition':
                yield Request(
                    url_to_trade, callback=self.parse_lot_auction, dont_filter=True, cb_kwargs={
                        'transfer': transfer, 'url_to_trade': url_to_trade, 'lot_number': lot_number, 'files': files,
                        'sources': sources, 'page_number': page_number, 'total_pages': total_pages
                    }
                )
        else:
            yield Request(
                lot_link, callback=self.parse_lot_tab, cb_kwargs={
                    'transfer': transfer,
                    'trading_type': trading_type,
                    'files': files,
                    'lots': lots,
                    'sources': sources, 'page_number': page_number, 'total_pages': total_pages,
                    'current_lot': current_lot
                },
                dont_filter=True
            )

    def parse_lot_offer(self, response, url_to_trade, transfer, lot_number, files: list, sources, page_number,
                        total_pages):
        """ parse lot with type - offer """
        combo = Combo(_response=response)
        loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', transfer['trading_form'])
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('msg_number', transfer['msg_number'])
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('address', transfer['address'])
        loader.add_value('region', transfer['region'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('status', combo.auc.get_lot_status())
        loader.add_value('lot_id', None)
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', lot_number)
        loader.add_value('short_name', combo.auc.get_short_name(lot_number))
        loader.add_value('lot_info', combo.auc.get_lot_info())
        loader.add_value('property_information', combo.auc.get_property_info())
        loader.add_value('start_price', combo.offer.get_start_price())
        lot_files = {'lot': []}
        _files = files
        gen = {'general': _files}
        total_files = dict(chain(gen.items(), lot_files.items()))
        loader.add_value('files', total_files)
        period_first_page = combo.offer.get_periods()
        total_pages_period = combo.offer.return_period_pagination()
        # total_pages_period & total are info about how many pages has pariod table
        if total_pages_period:
            total = copy.deepcopy(total_pages_period)
            del total_pages_period
        else:
            total = 1
        if total > 1:
            _form = copy.deepcopy(post_data_period_offer_page)
            rsl_selection = combo.pre.get_post_data_values(
                tag_html='input', post_argument='formMain:dataRSList_selection'
            )
            _form['formMain:dataRSList_selection'] = rsl_selection
            lot_viewstate2 = combo.pre.get_post_data_values('input', 'j_id1:javax.faces.ViewState:0')
            _form['javax.faces.ViewState'] = lot_viewstate2
            _form['formMain:inputServerTime'] = return_servertime()
            # param data depend from page number -> second page has value - 10
            _form['formMain:dataRSList_first'] = str(10 * 2 - 10)
            if combo.offer.get_refresh_form_j_idt55():
                _form['formMain:j_idt55'] = combo.offer.get_refresh_form_j_idt55()
            yield FormRequest(
                _link_post_period, callback=self.parse_period_offer_pages, formdata=_form, dont_filter=True,
                cb_kwargs={
                    'loader': loader, '_form': _form, 'periods_': period_first_page, 'current': 1, 'total': total,
                    'sources': sources, 'page_number': page_number
                }
            )
        else:
            loader.add_value('start_date_requests', combo.offer.get_start_date_request(period_first_page))
            loader.add_value('end_date_requests', combo.offer.get_end_date_request(period_first_page))
            loader.add_value('start_date_trading', combo.offer.get_start_date_request(period_first_page))
            loader.add_value('end_date_trading', combo.offer.get_end_date_request(period_first_page))
            loader.add_value('periods', period_first_page)
            loader.add_value('created_at', return_parse_date())
            yield loader.load_item()

    def parse_period_offer_pages(self, response, loader, _form, current, total, periods_: list, sources, page_number):
        combo = Combo(_response=response)
        next_periods: list = combo.offer.return_next_periods()
        periods_.extend(next_periods)
        if current < total:
            current += 1
            _form['formMain:dataRSList_first'] = str(10 * current - 10)
            _form['formMain:inputServerTime'] = return_servertime()
            yield FormRequest(
                _link_post_period, callback=self.parse_period_offer_pages, formdata=_form, dont_filter=True,
                cb_kwargs={
                    'loader': loader, '_form': _form, 'periods_': periods_, 'current': current, 'total': total,
                    'sources': sources, 'page_number': page_number
                }
            )
        else:
            loader.add_value('periods', periods_)
            loader.add_value('start_date_requests', combo.offer.get_start_date_request(periods_))
            loader.add_value('end_date_requests', combo.offer.get_end_date_request(periods_))
            loader.add_value('start_date_trading', combo.offer.get_start_date_request(periods_))
            loader.add_value('end_date_trading', combo.offer.get_end_date_request(periods_))
            loader.add_value('created_at', return_parse_date())
            yield loader.load_item()

    def parse_lot_auction(self, response, url_to_trade, transfer, lot_number, files, sources, page_number, total_pages):
        """ parse lot page of auction and competition """
        # with open('res_lot.txt', 'w') as f:
        #     f.write(response.text)
        combo = Combo(_response=response)
        loader = CrawlerBankruptItemLoader(CrawlerBankruptItem(), response=response)
        loader.add_value('data_origin', transfer['data_origin'])
        loader.add_value('trading_id', transfer['trading_id'])
        loader.add_value('trading_link', transfer['trading_link'])
        loader.add_value('trading_type', transfer['trading_type'])
        loader.add_value('trading_form', transfer['trading_form'])
        loader.add_value('trading_org', transfer['trading_org'])
        loader.add_value('trading_org_inn', transfer['trading_org_inn'])
        loader.add_value('trading_org_contacts', transfer['trading_org_contacts'])
        loader.add_value('trading_number', transfer['trading_number'])
        loader.add_value('msg_number', transfer['msg_number'])
        loader.add_value('case_number', transfer['case_number'])
        loader.add_value('debtor_inn', transfer['debtor_inn'])
        loader.add_value('address', transfer['address'])
        loader.add_value('region', transfer['region'])
        loader.add_value('arbit_manager', transfer['arbit_manager'])
        loader.add_value('arbit_manager_inn', transfer['arbit_manager_inn'])
        loader.add_value('arbit_manager_org', transfer['arbit_manager_org'])
        loader.add_value('start_date_requests', transfer['start_date_requests'])
        loader.add_value('end_date_requests', transfer['end_date_requests'])
        loader.add_value('start_date_trading', transfer['start_date_trading'])
        loader.add_value('end_date_trading', transfer['end_date_trading'])
        loader.add_value('status', combo.auc.get_lot_status())
        loader.add_value('lot_id', None)
        loader.add_value('lot_link', response.url)
        loader.add_value('lot_number', lot_number)
        loader.add_value('short_name', combo.auc.get_short_name(lot_number))
        loader.add_value('lot_info', combo.auc.get_lot_info())
        loader.add_value('property_information', combo.auc.get_property_info())
        loader.add_value('start_price', combo.auc.start_price_auction())
        loader.add_value('step_price', combo.auc.step_price_auction())
        lot_files = {'lot': list()}
        _files = files
        gen = {'general': _files}
        total_files = dict(chain(gen.items(), lot_files.items()))
        loader.add_value('files', total_files)
        loader.add_value('created_at', return_parse_date())
        yield loader.load_item()
