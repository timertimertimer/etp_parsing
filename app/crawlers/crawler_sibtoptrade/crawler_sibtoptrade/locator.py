#! -*- coding: utf-8 -*-
class Locator:
    # ##_BASIC__INFO_###
    LINKS_to_TRADING_pages = '//a[@href[contains(.,"optrade.ru/trade/")]]'

    form_data_start = '//div[contains(.,"Дата начала подачи заявок")]/following-sibling::div[@class="date-from-to"]//input/following::label[1][contains(.,"от")][1]'

    # ##_TRADING_PAGE_AUCTION_###
    foll_sibling = "/following::td[1]/text()"
    trade_type_loc = '//td[contains(.,"Вид торгов")]' + foll_sibling
    trade_form_loc = (
        '//td[contains(.,"рма представления предложений о цен")]' + foll_sibling
    )
    msg_num_loc = (
        '//td[contains(.,"омер объявления о проведении торгов на сайте")]'
        + foll_sibling
    )
    case_num_loc = '//td[contains(.,"омер дела о банкротстве")]' + foll_sibling
    # #########_________INFO________ABOUT_________ORGANIZATOR______#########
    trade_org_info_loc = 'normalize-space(//h3[contains(.,"нформация об организато")]'
    td_label_name = '/following::tr//following::td[contains(.,"олное наименование")]'
    org_name_loc = trade_org_info_loc + td_label_name + foll_sibling + ")"

    td_inn = '/following::tr//following::td[contains(.,"ИНН")]'
    inn_org = trade_org_info_loc + td_inn + foll_sibling + ")"

    td_email = '/following::tr//following::td[contains(.,"-mail")]'
    email_org_loc = trade_org_info_loc + td_email + foll_sibling + ")"

    td_phone = '/following::tr//following::td[contains(.,"онтактный телефо")]'
    phone_org_loc = trade_org_info_loc + td_phone + foll_sibling + ")"

    # ______DEBITOR_____________INFO###########:
    deb_info = 'normalize-space(//h3[contains(.,"нформация о должнике")]'
    td_deb_inn = '/following::tr//following::td[contains(.,"ИНН")]'
    debitor_inn = deb_info + td_deb_inn + foll_sibling + ")"
    td_deb_address = '/following::tr//following::td[contains(.,"Место нахождения")]'
    debitor_address = deb_info + td_deb_address + foll_sibling + ")"

    seller_info = 'normalize-space(//h3[contains(.,"нформация о продавце")]'
    td_seller_address = '/following::tr//following::td[contains(.,"Место нахождения")]'
    seller_address  = seller_info + td_seller_address + foll_sibling + ")"

    # ________ARBITR________INFO____________________
    arbitr_info = (
        'normalize-space(//h3[contains(.,"нформация об арбитражном управляю")]'
    )
    td_arb_name = '/following::tr//following::td[contains(.,"Фамилия Имя Отчество")]'
    arbitr_name_loc = arbitr_info + td_arb_name + foll_sibling + ")"
    td_arb_inn = '/following::tr//following::td[contains(.,"ИНН")]'
    arbitr_inn_loc = arbitr_info + td_arb_inn + foll_sibling + ")"
    td_arb_org = '/following::tr//following::td[contains(.,"Наименование СРО")]'
    arbitr_org_loc = arbitr_info + td_arb_org + foll_sibling + ")"

    # ##_LOT_INFO_###
    lot_info_loc = 'normalize-space(//h3[contains(text(),"Информация о лоте")]'
    lot_number_loc = (
        lot_info_loc
        + '/following::td[contains(.,"омер лота организатор")]'
        + foll_sibling
        + ")"
    )
    short_name = (
        lot_info_loc
        + '/following::td[contains(.,"писание (полное название лот")]'
        + foll_sibling
        + ")"
    )
    property_information_loc = (
        '//td[contains(.,"Сведения об имуществе (предприятии) должника, выставляемом на торги")]'
        + foll_sibling
    )

    start_price_loc = (
        '//h3[contains(text(),"Информация о лоте")]/following::td[contains(text(),"ачальная цена")]'
        + foll_sibling
    )
    step_price_loc = (
        lot_info_loc
        + '/following::td[contains(text(),"Шаг аукциона")]'
        + foll_sibling
        + ")"
    )
    step_if_bug = '//h3[contains(text(),"Информация о лоте")]/following::td[contains(text(),"Шаг аукциона")]/following::td[4]/text()'

    # ##_WORKING_WITH_PERIODS_###
    start_date_request_loc = (
        '//td[contains(.,"ата и время начала представления заяв")]' + foll_sibling
    )
    end_date_request_loc = (
        '//td[contains(.,"ата и время окончания представления заяв")]' + foll_sibling
    )
    start_trading_loc = (
        '//td[contains(text(),"ата и время начала торгов")]' + foll_sibling
    )
    end_trading_loc = (
        '//td[contains(text(),"ата и время окончания торго")]' + foll_sibling
    )
    extra_end_trading_loc = (
        '//td[contains(text(),"ата и время объявления результатов торгов")]'
        + foll_sibling
    )
    table_period_1 = (
        '//h3[contains(.,"График снижения цены")]/following::table[1]//tr[position()>1]'
    )

    # ##___offer__start/end___trading___#####
    lot_table_start_trade = '//h3[contains(.,"График снижения цены")]/following::table[1]//tr[position()>1][1]//td[1]/text()'
    lot_table_end_trade = '//h3[contains(.,"График снижения цены")]/following::table[1]//tr[position()>1][last()]//td[2]/text()'
