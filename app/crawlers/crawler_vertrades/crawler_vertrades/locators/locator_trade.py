class LocatorTrade:
    trading_number_loc = '//h1[@class="page_title"]'

    trading_type_loc = '//td[text()="Тип торгов"]/following-sibling::td[1]'
    status_loc = '//td[text()="Статус"]/following-sibling::td[1]'

    trading_org_loc = '//th[normalize-space(text())="Организатор торгов"]/ancestor::table[1]//td[normalize-space(text())="Наименование"]/following-sibling::td[1]'
    trading_org_inn_loc = '//th[normalize-space(text())="Организатор торгов"]/ancestor::table[1]//td[normalize-space(text())="ИНН"]/following-sibling::td'
    phone_org_loc = '//th[normalize-space(text())="Организатор торгов"]/ancestor::table[1]//td[normalize-space(text())="Номер контактного телефона"]/following-sibling::td'
    email_org_loc = '//th[normalize-space(text())="Организатор торгов"]/ancestor::table[1]//td[normalize-space(text())="Адрес электронной почты"]/following-sibling::td'

    msg_number_loc = '//th[normalize-space(text())="Информация для интеграции с ЕФРСБ"]/following::td[contains(text(), "торгов на ЕФРСБ")]/following-sibling::td'

    case_number_loc = (
        '//td[normalize-space(text())="Номер дела о банкротстве"]/following-sibling::td'
    )

    debitor_inn_loc = '//th[normalize-space(text())="Сведения о должнике"]/following::td[normalize-space(text())="ИНН" and following::th[normalize-space(text())="Финансовый управляющий"]]/following-sibling::td[1]'
    debitor_inn_loc_2 = '//th[normalize-space(text())="Сведения о должнике"]/following::td[normalize-space(text())="ИНН" and following::th[normalize-space(text())="Арбитражный управляющий"]]/following-sibling::td[1]'
    address_loc = '//th[normalize-space(text())="Сведения о должнике"]/following::td[normalize-space(text())="Адрес"]/following-sibling::td[1]'
    sud_loc = '//td[normalize-space(text())="Наименование арбитражного суда"]/following-sibling::td'
    arbitr_manag_loc = '//th[normalize-space(text())="Арбитражный управляющий"]/following::td[normalize-space(text())="ФИО" and following::th[normalize-space(text())="Информация для интеграции с ЕФРСБ"]]/following-sibling::td[1]'
    finance_manag_loc = '//th[normalize-space(text())="Финансовый управляющий"]/following::td[normalize-space(text())="ФИО" and following::th[normalize-space(text())="Информация для интеграции с ЕФРСБ"]]/following-sibling::td[1]'
    arbitr_inn_loc = '//th[normalize-space(text())="Арбитражный управляющий"]/following::td[normalize-space(text())="ИНН" and following::th[normalize-space(text())="Информация для интеграции с ЕФРСБ"]]/following-sibling::td[1]'
    finance_inn_loc = '//th[normalize-space(text())="Финансовый управляющий"]/following::td[normalize-space(text())="ИНН" and following::th[normalize-space(text())="Информация для интеграции с ЕФРСБ"]]/following-sibling::td[1]'
    arbitr_org_loc = '//th[normalize-space(text())="Арбитражный управляющий"]/following::td[normalize-space(text())="Название саморегулируемой организации" and following::th[normalize-space(text())="Информация для интеграции с ЕФРСБ"]]/following-sibling::td[1]'
    finance_org_loc = '//th[normalize-space(text())="Финансовый управляющий"]/following::td[normalize-space(text())="Название саморегулируемой организации" and following::th[normalize-space(text())="Информация для интеграции с ЕФРСБ"]]/following-sibling::td[1]'
    start_date_requests_loc = '//td[normalize-space(text())="Начало предоставления заявок на участие"]/following-sibling::td'
    end_date_requests_loc = '//td[normalize-space(text())="Окончание предоставления заявок на участие"]/following-sibling::td'
    general_files_loc = '//th[normalize-space(text())="Электронные документы"]/ancestor::table[@class="main-table col-2"]//a[@target="_blank"]'

    lots_loc = '//table[contains(@class, "lottab")]'
    lot_number_loc = "//th"
