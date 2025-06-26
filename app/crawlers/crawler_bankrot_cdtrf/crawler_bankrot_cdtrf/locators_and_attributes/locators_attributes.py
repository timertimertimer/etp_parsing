class LocatorMain:
    ToolkitScriptManager1_first_query = r"ctl00$cph1$upList|ctl00$cph1$btFilter"
    ToolkitScriptManager1_Hidden = r"ctl00_ToolkitScriptManager1_HiddenField"
    EVENTTARGET_1st_post = r"ctl00$cph1$btFilter"
    EVENTTARGET_next_page = r"ctl00$cph1$pgvTrades$ctl22$lnkNext"

    trading_links_loc = '//a[@id[contains(.,"ctl00_cph1_pgvTrades_")]]/ancestor::td[1]//@href[contains(.,"/card/trade.aspx?id=")]'
    trading_number_loc = '//div[@class="table-content"]//td[contains(., "Код торгов")]/following-sibling::td[1]'
    trading_type_loc = '//div[@class="table-content"]//td[contains(., "орма проведения торго")]/following-sibling::td[1]'
    trading_form_loc = '//div[@class="table-content"]//td[contains(., "орма представления предложений")]/following-sibling::td[1]'
    trading_status_loc = '//div[@class="table-content"]//td[contains(., "Статус торгов")]/following-sibling::td[1]'

    trading_org_company_loc = '//div[@class="table-content"]//tr//td[contains(., "ведения об организаторе торго")]//following::tr[1]'

    # bs4 attributes
    # trading organizator <tr> "id" -> if company
    list_of_company_id = '//tr[contains( @ id, "ctl00_cph1_trOrgJur")]'
    org_email_loc = "ctl00_cph1_lOrgEmail"
    phone_org_loc = '//*[contains(@id, "ctl00_cph1_lOrgEmail")]/following::td[contains(.,"омер контактного телефона")]//following-sibling::td[1]'
    org_tr_id_com_name = "#ctl00_cph1_trOrgJur1"
    org_tr_id_inn = "ctl00_cph1_trOrgJur3"

    # trading organizer <tr>
    list_person_info_id = '//tr[contains(@id, "ctl00_cph1_trOrgNat")]'
    org_person_id_lastname = "ctl00_cph1_trOrgNat1"
    org_person_id_firstname = "ctl00_cph1_trOrgNat2"
    org_person_id_middlename = "ctl00_cph1_trOrgNat3"
    org_person_id_inn = "ctl00_cph1_trOrgNat4"

    msg_id_loc = "ctl00_cph1_trIDEFRSB"
    case_number_id_loc = "ctl00_cph1_trDealNum"

    list_debtor_id = '//tr[contains(@id, "ctl00_cph1_trDebt")]'
    sud_loc = '//tr[contains(@id, "ctl00_cph1_trDealArbJud")]'

    list_arbitr_id = '//tr[contains(@id, "ctl00_cph1_trArbMan")]'
    short_name_id_loc = "ctl00_cph1_lName"
    lot_info_id_loc = "ctl00_cph1_lLotInfo"
    property_info_if_loc = "ctl00_cph1_lLotProcedure"

    # FILES
    to_lot_files_loc = '//div[@class="table-content"]//tr//td[contains(., "Фотографии")]//following-sibling::td[1]/a'
    to_dohovor_loc = '//div[@class="table-content"]//tr//td[contains(., "Договор о задатк")]//following-sibling::td[1]/a'
    to_proekt_loc = '//div[@class="table-content"]//tr//td[contains(., "роект договора купли-продаж")]//following-sibling::td[1]/a'


class Offer(LocatorMain):
    def __init__(self):
        super().__init__()

    period_table = '//tr[@id="ctl00_cph1_trLotSchedules"]/ancestor::table[1]'


class Auction(LocatorMain):
    def __init__(self):
        super().__init__()

    start_date_req_loc = "ctl00_cph1_lRequestTimeBegin"
    end_date_req_loc = "ctl00_cph1_lRequestTimeEnd"
    start_date_trading = "ctl00_cph1_lAuctionTimeBegin"
    extra_start_date_trading = "ctl00_cph1_lWinnerTime"
    end_date_trading = "ctl00_cph1_lAuctionTimeEnd"

    start_price_auc_loc = "ctl00_cph1_lPriceBegin"
    step_price_auc_loc = "ctl00_cph1_trIncreasePrice"
