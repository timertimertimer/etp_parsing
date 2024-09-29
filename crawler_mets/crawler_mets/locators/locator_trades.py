# -*- coding: utf-8 -*-
class LocatorOffer:
    trading_number_loc = '//h3[contains(.,"идентификационный")]'
    trading_organ_loc = '//th[contains(.,"рганизатор торгов")]/following::td[1][contains(text(),"аименование")]/following-sibling::td'
    email_organ_loc = '//th[contains(.,"рганизатор торгов")]/following::td[contains(text(),"дрес электронной почты")]/following-sibling::td[1]'
    phone_organ_loc = '//th[contains(.,"рганизатор торгов")]/following::td[contains(text(),"телефона")]/following-sibling::td[1]'
    msg_number_loc = '//td[contains(., "оргов на ЕФРСБ")]/following-sibling::td[1]'
    case_number_loc = '//td[contains(., "омер дела о банкротстве")]/following-sibling::td[1]'
    debitor_inn_loc = '//th[contains(.,"едения о должнике")]/following::td[contains(text(),"ИНН")]/following-sibling::td[1]'

    # get text of <th> with lot number
    count_lots_loc = '//a[contains(@name, "lot")]/ancestor::table'

    arbitr_manag_loc = '//th[contains(.,"ражный управляющий")]/following::td[contains(text(),"ФИО")]/following-sibling::td[1]'
    finance_manag_loc = '//th[contains(.,"инансовый управляющий")]/following::td[contains(text(),"ФИО")]/following-sibling::td[1]'
    arbitr_inn_loc = '//th[contains(.,"ражный управляющий")]/following::td[contains(text(),"ИНН")]/following-sibling::td[1]'
    finance_inn_loc = '//th[contains(.,"инансовый управляющий")]/following::td[contains(text(),"ИНН")]/following-sibling::td[1]'
    arbitr_org_loc = '//th[contains(.,"ражный управляющий")]/following::td[contains(text(),"азвание саморегулируемой организаци")]/following-sibling::td[1]'
    finance_org_loc = '//th[contains(.,"инансовый управляющий")]/following::td[contains(text(),"азвание саморегулируемой организаци")]/following-sibling::td[1]'

    status_loc = '//th[contains(., "по лоту №{}")]/ancestor::table/following-sibling::table//td[contains(text(), "татус торгов")][1]/following-sibling::td[1]'
    short_name_loc = '//th[contains(., "по лоту №{}")]/ancestor::table/following-sibling::table//td[contains(text(),"раткие сведения об имуществе")]/following-sibling::td[1]'
    lot_info_loc = '//th[contains(., "по лоту №{}")]/ancestor::table/following-sibling::table//td[contains(text(),"Cведения об имуществе")]/following-sibling::td[1]'
    property_info_loc = '//th[contains(., "по лоту №{}")]/ancestor::table/following-sibling::table//td[contains(text(),"орядок ознакомления с имуществом")]/following-sibling::td[1]'
    start_price_loc = '//th[contains(., "по лоту №{}")]/ancestor::table/following-sibling::table//td[contains(text(),"ачальная цена продаж")]/following-sibling::td[1]'
    period_table_loc = '//th[contains(., "по лоту №{}")]/ancestor::table/following-sibling::table//td[contains(text(),"рафик снижения цены")]//following-sibling::td/table'
    # period_table_loc_2 = '//th[contains(., "по лоту №{}")]/ancestor::table/following-sibling::table//td[contains(text(),"рафик снижения цены")]//following-sibling::td/table'

    file_lot_link_loc = '//th[contains(., "Сведения по лоту №{}")]/ancestor::table//div[@class="fileview"]//a[' \
                        'contains(@href,"download")]'
    general_files_loc = '//th[contains(., "Электронные документы")]/ancestor::table[not(contains(.,"ведения по лоту"))]//a[contains(@href,"download")]'

class LocatorAuction:
    step_price_loc = '//td[contains(.,"еличина повышения начальной")]/following-sibling::td[1]'

    start_date_request_loc = '//th[contains(., "Информация о торгах")]/ancestor::table//td[contains(text(),"ачало предоставления заявок на участи")]/following-sibling::td[1]'
    end_date_request_loc = '//th[contains(., "Информация о торгах")]/ancestor::table//td[contains(text(),"кончание предоставления заявок на участи")]/following-sibling::td[1]'
    start_date_trading_loc = '//th[contains(., "Информация о торгах")]/ancestor::table//td[contains(text(),"ачало подачи предложений о цене имуществ")]/following-sibling::td[1]'
    end_date_trading_loc = '//th[contains(., "Информация о торгах")]/ancestor::table//td[contains(text(),"ата и время подведения результатов торго")]/following-sibling::td[1]'