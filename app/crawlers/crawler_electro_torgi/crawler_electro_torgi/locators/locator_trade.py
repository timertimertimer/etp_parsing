class LocatorTrade:
    trading_type_and_form_loc = (
        '//div[normalize-space(text())="Номер торгов"]/following-sibling::div[1]/text()'
    )
    trading_org_loc = (
        '//div[normalize-space(text())="Наименование"]/following-sibling::div[1]/text()'
    )
    trading_org_loc_2 = '//div[normalize-space(text())="Организатор торгов"]/following-sibling::div[1]/text()'
    trading_org_inn_loc = '(//div[.//small[normalize-space(text())="ИНН:"]]/following-sibling::div[1])[1]/text()'
    phone_org_loc = '//div[normalize-space(text())="Номер контактного телефона"]/following-sibling::div[1]/text()'
    email_org_loc = '//div[normalize-space(text())="Адрес электронной почты"]/following-sibling::div[1]/text()'
    msg_number_loc = '//div[normalize-space(text())="Идентификационный номер торгов на ЕФРСБ"]/following-sibling::div[1]/text()'
    case_number_loc = '//div[normalize-space(text())="Номер дела о банкротстве"]/following-sibling::div[1]/text()'
    debitor_inn_loc = '//div[normalize-space(text())="Сведения о должнике"]/following::div[contains(text(), "ИНН") and following::div[contains(text(), "Сведения о банкротстве")]]/following-sibling::div/text()'
    debitor_inn_loc_2 = '(//div[normalize-space(text())="Должник(и)"]/following::div[contains(text(), "ИНН")]/following-sibling::div/text())'
    region_loc = '//div[normalize-space(text())="Сведения о банкротстве"]/following::div[contains(text(), "Наименование арбитражного суда")]/following-sibling::div/text()'
    arbit_manager_loc = '//div[normalize-space(text())="Фамилия, имя, отчество"]/following-sibling::div[1]/text()'
    arbit_manager_inn_loc = '//div[normalize-space(text())="Арбитражный управляющий"]/following::div[contains(text(), "ИНН") and following::div[contains(text(), "Сведения о должнике")]]/following-sibling::div/text()'
    arbit_manager_org_loc = '//div[contains(normalize-space(text()), "Название саморегулируемой организации")]/following-sibling::div/text()'
    status_loc = (
        '//div[normalize-space(text())="Статус торгов"]/following-sibling::div[1]'
    )

    files_loc = "//div[@data-file-id]"
    lots_loc = '//div[@id="lots"]//div[@class="row"]'
    short_name_loc = '//div[normalize-space(text())="Наименование лота"]/following-sibling::div[1]/text()'
    short_name_loc_2 = (
        '//div[contains(@class, "grey-grib") and contains(@class, "bold")]/text()'
    )
    lot_info_loc = '//div[normalize-space(text())="порядок ознакомления с имуществом"]/following-sibling::div[1]/text()'
    lot_info_loc_2 = '//div[contains(., "орядок ознакомления с имуществом")]/following-sibling::div[1]/text()'
    property_information_loc = '//div[contains(normalize-space(text()), "Порядок оформления участия в торгах")]/following-sibling::div/text()'
    start_date_requests_loc = '//div[contains(normalize-space(text()), "Начало приема заявок")]/following-sibling::div[1]/text()'
    end_date_requests_loc = '//div[contains(normalize-space(text()), "Окончание приема заявок")]/following-sibling::div[1]/text()'
    start_price_auc_loc = '//div[contains(normalize-space(text()), "Начальная цена")]/following-sibling::div[1]/text()'
    step_price_auc_loc = '//div[contains(normalize-space(text()), "Шаг увеличения цены")]/following-sibling::div[1]/text()'
    categories_loc = '//div[contains(normalize-space(text()), "Тип имущества")]/following-sibling::div[1]/text()'
