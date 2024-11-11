class LocatorOffer:

    pagination_lot_page = '//div[contains(@class, "pages_number")]//ul[contains(@class,"pagination")]'
    offer_trading_number_loc = '//div[contains(text(),"явка на проведение торг")]'
    offer_trading_number_loc2 = '//div[contains(text(),"Процедурная часть")]'

    offer_trading_type_loc1 = '//div[contains(text(),"пособ проведения процедуры")]/following-sibling::div[1]'
    offer_trading_type_loc2 = '//div[contains(text(),"пособ проведения ТП")]/following-sibling::div[1]'
    offer_trading_type_loc3 = '//div[contains(text(),"пособ проведения")]/following-sibling::div[1]'

    # _trading_organizer_###
    org_div_loc = '//div[contains(text(),"нформация об организато")]'
    offer_org_name_loc1 = org_div_loc + '/ancestor::div[1]//strong[contains(text(),"Полное наименование")]/following::text()[1]'
    offer_org_name_loc2 = org_div_loc + '/ancestor::div[1]//a'
    offer_org_inn_loc = org_div_loc + '/ancestor::div[1]//strong[contains(text(),"ИНН")]/following::text()[1]'
    offer_org_email_loc = org_div_loc + '/ancestor::div[1]//strong[contains(text(),"mail")]/following::text()[1]'
    offer_org_phone_loc = org_div_loc + '/ancestor::div[1]//strong[contains(text(),"елефон")]/following::text()[1]'

    offer_msg_number_loc = '//div[contains(text(),"сообщения на ЕФРСБ")]/following-sibling::div[1]/text()'
    offer_case_number = '//div[contains(text(),"омер дела о банкротств")]/following-sibling::div[1]'

    # _debitor_#
    deb_div_loc = '//div[contains(text(),"Должник")]/ancestor::div[1]'
    deb_inn_loc = deb_div_loc + '//strong[contains(text(),"ИНН")]/following::text()[1]'

    # _arbitr_#
    arbitr_last_name = '//div[contains(text(),"Фамилия арбитражного")]/following-sibling::div[1]'
    arbitr_name = '//div[contains(text(),"Имя арбитражного")]/following-sibling::div[1]'
    arbitr_mid_name = '//div[contains(text(),"Отчество арбитражного")]/following-sibling::div[1]'
    arbitr_org = '//div[contains(text(),"СРО, членом которого является арбитражный")]/following-sibling::div[1]'
    arbitr_inn = '//div[contains(text(),"ИНН арбитражного")]/following-sibling::div[1]'

    div_info_lot_offer = '//div[contains(@class,"panel panel-default panel-striped")]'

    # _PERIOD TABLES
    period_tables_loc = '//div[@id="{}"]/ancestor::div[1]//table'

    # get locator of link to document page
    doc_link_loc = 'a[href *= "/procedure/documentation"]'
    old_table_doc_general = '//div[contains(.,"Документация")]/following::div[@class != "documentation_{}"]/table[1]//tbody/tr'
    doc_proc_table = '//td[contains(@class, "procedure-document")]/ancestor::table/tbody/tr'
    # count proc documents
    doc_proc_num_loc = '//a[@href[contains(.,"proc")]]/ancestor::li//span[@title]/text()'


    # lot -documents
    count_lot_doc_loc = '//li/a[contains(@href,"lot")]'
    doc_lot_amount_loc = '//a[@href[contains(.,"lot")]]/ancestor::li//span[@title]/text()'
    lot_doc_table = '//div[@class="documentation_{}"]//table/tbody/tr'
