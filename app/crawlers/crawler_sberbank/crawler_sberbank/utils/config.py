from datetime import datetime, timedelta
from pathlib import Path

from app.utils.datetime_helper import (
    DateTimeHelper
)

data_origin_url = "https://utp.sberbank-ast.ru/"
main_url_start = "https://utp.sberbank-ast.ru/Bankruptcy/List/BidList"
part_path_to_trade = r"PurchaseView"
part_path_to_lot = r"BidView"
days = 7
start_date = DateTimeHelper.format_datetime(
    datetime.now(DateTimeHelper.moscow_tz) - timedelta(days=days), "%Y-%m-%d"
)
# format period
# W - week
# D - day
format_period = "D"
# periods - how many weeks or days been iteration - FREQUENCY (freq)
periods_ = 1
Referer = "https://utp.sberbank-ast.ru/Bankruptcy/List/BidList"
pattern_lots_links = r" <objectHrefTerm>(.*?)</objectHrefTerm>"
first_part_link = "https://utp.sberbank-ast.ru/Bankruptcy/File/DownloadFile?fid="
xml_data = "<elasticrequest><filters><mainSearchBar><value></value><type>best_fields</type><minimum_should_match>100%</minimum_should_match></mainSearchBar><purchAmount><minvalue></minvalue><maxvalue></maxvalue></purchAmount><PublicDate><minvalue>{start_date}</minvalue><maxvalue>{end_date}</maxvalue></PublicDate><PurchaseStageTerm><value></value><visiblepart></visiblepart></PurchaseStageTerm><RegionNameTerm><value></value><visiblepart></visiblepart></RegionNameTerm><DebtorINNnGram><value></value></DebtorINNnGram><DebtorName><value></value></DebtorName><IsPledgeTerm><checkbox></checkbox><value></value></IsPledgeTerm><RequestStartDate><minvalue></minvalue><maxvalue></maxvalue></RequestStartDate><RequestDate><minvalue></minvalue><maxvalue></maxvalue></RequestDate><AuctionBeginDate><minvalue></minvalue><maxvalue></maxvalue></AuctionBeginDate><okdp2MultiMatch><value></value></okdp2MultiMatch><okdp2tree><value></value><productField></productField><branchField></branchField></okdp2tree><classifier><visiblepart></visiblepart></classifier><orgCondition><value></value></orgCondition><orgDictionary><value></value></orgDictionary><organizator><visiblepart></visiblepart></organizator><PurchaseTypeNameTerm><value></value><visiblepart></visiblepart></PurchaseTypeNameTerm><statistic><totalProc>{total_lot}</totalProc><TotalSum>{total_sum}</TotalSum><DistinctOrgs>{total_org}</DistinctOrgs></statistic></filters><fields><field>TradeSectionId</field><field>purchAmount</field><field>CurrentAmount</field><field>purchCurrency</field><field>purchCodeTerm</field><field>PurchaseTypeName</field><field>BidStatusName</field><field>OrgName</field><field>SourceTerm</field><field>PublicDate</field><field>RequestDate</field><field>RequestStartDate</field><field>RequestAcceptDate</field><field>bankrAuctionStartDate</field><field>CreateRequestHrefTerm</field><field>CreateRequestAlowed</field><field>purchName</field><field>SourceHrefTerm</field><field>objectHrefTerm</field><field>ReqCnt</field><field>BidName</field><field>PurchaseTypeId</field><field>auctResultDate</field><field>needPayment</field><field>PurchaseTypeType</field></fields><sort><value>default</value><direction></direction></sort><aggregations><empty><filterType>filter_aggregation</filterType><field></field><min_doc_count>0</min_doc_count><order>asc</order></empty></aggregations><size>{amount_lot_on_page}</size><from>{from_number}</from></elasticrequest>"
with open(Path(__file__).parent / "request.xml", encoding="utf-8") as file:
    xml_request_data = file.read().replace("\n", "").replace(" ", "")
