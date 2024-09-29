class LocatorAuction:
    following_td = '/following::td[1]'
    trading_form_loc = '//td[contains(text(),"Форма аукциона")]/following::td[1]/text()'
    trading_org_loc = '//td[contains(text(),"Организатор процедуры")]' + following_td
    trading_org_inn = '//tr/td[contains(text(), "ИНН")]/following-sibling::td[1]'
    organiz_phone_loc = '//tr/td[contains(text(), "елефоны и факсы организаци")]//following::tr[1]/td[last()]'

    msg_number_loc = '//td[contains(text(),"сообщения на ЕФРСБ")]/following::td[1]'
    case_number_loc = '//td[contains(text(), "Номер дела о")]/following-sibling::td[1]'

    debtor_inn_loc = '//td[contains(text(),"Должник")]/following::td[1]/text()'

    arbitr_manager_loc = '//td[contains(text(),"рбитражный управляющий")]/following-sibling::td[1]/text()'
    arbitr_org_loc = '//td[contains(text(),"СРО, членом которой является арбитражн")]/following-sibling::td[1]/text()'

    ####__LOT__INFO__####
    short_name_loc = '//td[contains(text(),"Предмет договора (ОКПД2")]' + following_td
    property_information_loc = '//td[contains(text(),"орядок ознакомления с имущество")]' + following_td

    start_date_request_auc_loc = '//td[contains(text(),"ата публикации в МТС")]' + following_td
    end_date_request_auc_loc = '//td[contains(text(),"ата окончания приема Аукционных заявок в аукцио")]' + following_td
    start_date_trading_loc = '//td[contains(text(),"ата начала аукциона")]' + following_td
    end_date_trading_loc = '//td[contains(text(),"ата и время подведения итогов")]' + following_td

    start_price_loc = '//td[contains(text(),"ачальная цена предмета")]/following::td[1]'
    step_price_loc = '//td[contains(text(),"Шаг аукцион")]/following::td[1]'

    # _documentation
    link_to_doc_page_loc = '//a[text()="Документация по торгам"]'
    doc_table_auc_loc = '//table[@class="list"]'
    doc_table_auc_loc_2 = '//table[@class="list document_list"]'
