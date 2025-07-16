from app.utils.config import *


def return_auction_link(_data_origin):
    auction_link = "public/auctions-all/"
    return _data_origin + auction_link


def return_offer_link(_data_origin):
    offer_link = "public/public-offers-all/"
    return _data_origin + offer_link


def return_compet_link(_data_origin):
    competition_link = "public/contests-all/"
    return _data_origin + competition_link


# очень важно иметь дату без нулей в начале дня и месяца, иначе неправильно работает фильтрация
current_date = datetime.now()
one_month_ago = current_date - timedelta(days=30)
start_date = f"{one_month_ago.year}-{one_month_ago.month}-{one_month_ago.day} 0:0:-1"
data_origin = {
    "alfalot": "https://bankrupt.alfalot.ru/",
    "arbbitlot": "https://torgi.arbbitlot.ru/",
    "arbitat": "http://arbitat.ru/",
    "bepspb": "https://bankruptcy.bepspb.ru/",
    "centerr_bankrupt": "https://bankrupt.centerr.ru/",
    "centerr_business": "https://business.centerr.ru/",
    "etpu": "https://bankrupt.etpu.ru/",
    "etpugra": "http://etpugra.ru/",
    "ets24": "http://bankrupt.ets24.ru/",
    "gloriaservice": "https://gloriaservice.ru/",
    "meta_invest": "https://meta-invest.ru/",
    "propertytrade": "https://propertytrade.ru/",
    "selt_online": "https://selt-online.ru/",
    "tender_one": "https://bankrupt.tender.one/",
    "tendergarant": "https://tendergarant.com/",
    "torgibankrot": "https://torgibankrot.ru/",
    "utender": "http://utender.ru/",
    "utpl": "https://bankrupt.utpl.ru/",
    "zakazrf": "http://bankrot.zakazrf.ru/",
}

urls = {
    "alfalot": "https://bankrupt.alfalot.ru/",
    "arbbitlot": "https://torgi.arbbitlot.ru/",
    "arbitat": "http://arbitat.ru/",
    "bepspb": "https://bankruptcy.bepspb.ru/",
    "centerr_bankrupt": "https://bankrupt.centerr.ru/",
    "centerr_business": "https://business.centerr.ru/",
    "etpu": "https://etpu.ru/",
    "etpugra": "http://etpugra.ru/",
    "ets24": "http://ets24.ru/",
    "gloriaservice": "https://gloriaservice.ru/",
    "meta_invest": "https://meta-invest.ru/",
    "propertytrade": "https://propertytrade.ru/",
    "selt_online": "https://selt-online.ru/",
    "tender_one": "https://bankrupt.tender.one/",
    "tendergarant": "https://tendergarant.com/",
    "torgibankrot": "https://torgibankrot.ru/",
    "utender": "http://utender.ru/",
    "utpl": "https://bankrupt.utpl.ru/",
    "zakazrf": "http://bankrot.zakazrf.ru/",
}

common_data = {
    "__EVENTTARGET": "",
    "__EVENTARGUMENT": "",
    "__VIEWSTATE": "",
    "__SCROLLPOSITIONX": "0",
    "__SCROLLPOSITIONY": "0",
    "__EVENTVALIDATION": "",
    "__CVIEWSTATE": "",
    "ctl00$ctl00$LeftContentLogin$ctl00$Login1$UserName": "",
    "ctl00$ctl00$LeftContentLogin$ctl00$Login1$Password": "",
    "ctl00$ctl00$LeftContentSideMenu$mSideMenu$extAccordionMenu_AccordionExtender_ClientState": "0",
}

common_post_data = {
    **common_data,
    "ctl00$ctl00$BodyScripts$BodyScripts$scripts": "ctl00$ctl00$MainExpandableArea$phExpandCollapse$UpdatePanel1|ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_lotNumber_лота": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_lotTitle_Наименованиелота": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$Party_contactName_AliasFullOrganizerTitle": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_InitialPrice_Начальнаяценаотруб": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$Party_inn_ИННорганизатора": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_ParticipationFormID_Форматоргапосоставуучастников": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$Party_kpp_КППорганизатора": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$Party_registeredAddress_Адресрегистрацииорганизатора": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_BankruptName_Должник": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_purchaseStatusID_Статус": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_BankruptINN_ИННдолжника": "",
    "__ASYNCPOST": "true",
}

post_data_auction = {
    **common_post_data,
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_Датапроведенияпо_dateInput": "0-0-0 -1:-1:-1",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_purchaseNumber_аукциона": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_fullTitle_Наименованиеаукциона": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton": "Искать аукционы",
}

post_data_offer = {
    **common_post_data,
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_purchaseNumber_публичногопредложения": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_fullTitle_Наименованиепубличногопредложения": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_bidSubmissionStartDate_Датаначалапредставлениязаявокнаучастиепо_dateInput": "0-0-0 -1:-1:-1",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton": "Искать публичные предложения",
}

post_data_competition = {
    **common_post_data,
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_auctionStartDate_Датапроведенияпо_dateInput": "0-0-0 -1:-1:-1",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_purchaseNumber_конкурса": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$PurchasesSearchCriteria$vPurchaseLot_fullTitle_Наименованиеконкурса": "",
    "ctl00$ctl00$MainExpandableArea$phExpandCollapse$SearchButton": "Искать конкурсы",
}

script_lua_nojs = """
         function main(splash)
         splash:on_request(function(request)
             if request.url:find('css') then
                 request.abort()
                 end
             end)
             splash.images_enabled=false
             -- splash:autoload("https://code.jquery.com/jquery-1.7.1.min.js")
             splash.private_mode_enabled = false
             -- splash.plugins_enabled = false
             splash.js_enabled = false
             splash:init_cookies(splash.args.cookies)
	         assert(splash:wait(1))
             assert(splash:go{
             splash.args.url,
             -- headers=splash.args.headers,
             http_method=splash.args.http_method,
             --  body=splash.args.body,
             })
             assert(splash:wait(4))
             -- local entries = splash:history()
            --  local last_response = entries[#entries].response
             -- splash:runjs("window.scrollTo(0,document.body.scrollHeight);")
             assert(splash:wait(2))
             return {
                 -- headers = last_response.headers,
                 cookies = splash:get_cookies(),
                 html = splash:html(),
                 }
         end
                 """
