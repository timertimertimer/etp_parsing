class LocatorTradePage:
    # !!!!! locator for aukcioncenter ru
    check_date = '//th[contains(., "нформация о торгах")]/ancestor::table[1]//td[contains(., "ачало предоставления заявок")]/following-sibling::td[1]'

    trading_type_loc = '//th[contains(., "Информация о торгах")]/following::td[contains(text(), "орма проведения торгов и подач")]/following-sibling::td[1]'

    number_of_total_pages_loc = r'//a[@class="paginatorNotSelectedPage"][last()]/text()'
    current_page_loc = '//span[@class="paginatorSelectedPage"]'

    h1_trading_number_loc = "//h1"

    trading_org_name_loc = '//th[contains(., "рганизатор торгов")]/ancestor::table[1]//td[contains(., "Наименование")]//following-sibling::td[1]'
    trading_org_email_loc = '//th[contains(., "рганизатор торгов")]/ancestor::table[1]//td[contains(., "дрес электронной почт")]//following-sibling::td[1]'
    trading_org_phone_loc = '//th[contains(., "рганизатор торгов")]/ancestor::table[1]//td[contains(., "омер контактного телефо")]//following-sibling::td[1]'

    arbitr_name_loc = '//th[contains(., "рбитражный управляющи")]/ancestor::table[1]//td[contains(., "амилия")]//following-sibling::td[1]'
    arbitr_org_loc = '//th[contains(., "рбитражный управляющи")]/ancestor::table[1]//td[contains(., "азвание саморегулируемой организаци")]//following-sibling::td[1]'
    competiton_man = '//th[contains(., "редставитель конкурсного управляюще")]/ancestor::table[1]//td[contains(., "амилия")]//following-sibling::td[1]'

    msg_number_loc = '//th[contains(., "нформация для интеграции с ЕФРС")]/ancestor::table[1]//td[contains(., "омер торгов на ЕФРСБ")]//following-sibling::td[1]'
    case_number_loc = '//th[contains(., "ведения о банкротств")]/ancestor::table[1]//td[contains(., "омер дела о банкротств")]//following-sibling::td[1]'
    debtor_inn_loc = '//th[contains(., "ведения о должник")]/ancestor::table[1]//td[contains(., "ИНН")]//following-sibling::td[1]'
    address_loc = '//th[contains(., "ведения о банкротств")]/ancestor::table[1]//td[contains(., "аименование арбитражного суд")]//following-sibling::td[1]'

    # dates of events of auction and competition
    start_date_request_loc = '//th[contains(., "нформация о торга")]/ancestor::table[1]//td[contains(., "ачало предоставления заявок на уча")]//following-sibling::td[1]'
    end_date_request_loc = '//th[contains(., "нформация о торга")]/ancestor::table[1]//td[contains(., "кончание предоставления заявок на уч")]//following-sibling::td[1]'
    start_date_trading_loc = '//th[contains(., "нформация о торга")]/ancestor::table[1]//td[contains(., "ачало подачи предложений о цене им")]//following-sibling::td[1]'
    end_date_trading_loc = '//th[contains(., "нформация о торга")]/ancestor::table[1]//td[contains(., "ата и время подведения результатов торг")]//following-sibling::td[1]'

    files_data_loc = '//tr[not(contains(., "ачать все прилож"))]//a'
