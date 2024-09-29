class LoacatorAuction:
    count_lots = 'a[href *= "/Bankruptcy/NBT/BidView"]'
    trading_number_loc = '//tr//td[contains(text(),"Код торгов")]/following-sibling::td[1]'
    trading_organ_loc = '//th[contains(text(),"ведения об организаторе торгов")]/ancestor::table[1]//tr/td[contains(' \
                        'text(), "Наименование")]/following-sibling::td[1]'
    trading_organ_inn_loc = '//th[contains(text(),"ведения об организаторе торгов")]/ancestor::table[1]//tr/td[contains(' \
                        'text(), "ИНН")]/following-sibling::td[1]'

    trading_org_phone_loc = '//th[contains(text(),"ведения об организаторе торгов")]/ancestor::table[1]//tr/td[contains(text(),"онтактный телефон")]/following-sibling::td[1]'
    trading_org_email_loc = '//th[contains(text(),"ведения об организаторе торгов")]/ancestor::table[1]//tr/td[contains(text(),"лектронный адрес")]/following-sibling::td[1]'

    case_number_loc = '//th[contains(text(),"ведения об арбитражном суд")]/ancestor::table[1]//tr/td[contains(text(),"омер дела о банкротств")]/following-sibling::td[1]'

    debitor_inn_loc = '//th[contains(text(),"ведения о должнике")]/ancestor::table[1]//tr/td[contains(text(), "ИНН")]/following-sibling::td[1]'

    arbitr_manager_loc = '//th[contains(text(),"ведения об арбитражном")]/ancestor::table[1]//tr/td[contains(text(),"ФИО")]/following-sibling::td[1]'
    arbitr_inn_loc = '//th[contains(text(),"ведения об арбитражном")]/ancestor::table[1]//tr/td[contains(text(), "ИНН")]/following-sibling::td[1]'
    arbitr_org_loc = '//th[contains(text(),"ведения об арбитражном")]/ancestor::table[1]//tr/td[contains(text(), "аморегулируемая организация арбитражн")]/following-sibling::td[1]'

    start_date_request_loc = '//td[contains(text(), "ата и время начала подачи заяво")]/following-sibling::td[1]'
    end_date_request_loc = '//td[contains(text(), "ата и время окончания подачи заяво")]/following-sibling::td[1]'
    start_date_trading_loc = '//td[contains(text(), "ата и время начала торгов")]/following-sibling::td[1]'
    end_date_trading_loc = '//td[contains(text(), "ата и время подведения результатов торг")]/following-sibling::td[1]'

    lot_number_loc = '//td[contains(.,"Номер лота")]/following-sibling::td[1]'
    short_name_loc = '//th[contains(.,"Информация по лоту")]/ancestor::table[1]//td[contains(text(),"аименовани")]/following-sibling::td[1]'
    lot_info_loc =  '//th[contains(.,"Сведения о должнике")]/ancestor::table[1]//td[contains(text(),"Сведения об имуществе (предприятии) должника")]/following-sibling::td[1]'
    property_info = '//th[contains(.,"Сведения о должнике")]/ancestor::table[1]//td[contains(text(),"Порядок ознакомления с имуществом")]/following-sibling::td[1]'

    start_price_loc = '//th[contains(.,"орядок проведения торгов")]/ancestor::table[1]//td[contains(text(),"Начальная цена продажи")]/following-sibling::td[1]'
    step_price_loc = '//th[contains(.,"орядок проведения торгов")]/ancestor::table[1]//td[contains(text(),"аг торгов")]/following-sibling::td[1]'

class LocatorOffer:
    start_price_loc = '//th[contains(.,"орядок проведения торгов")]/ancestor::table[1]//td[contains(text(),"ачальная цена")]/following-sibling::td[1]'
    period_table_loc = '//th[contains(.,"Дата и время начала периода")]/ancestor::table[1]'
    file_gen_loc = '//a[@href="javascript:empty();"]//text()'

class LocatorCompetition:
    pass
