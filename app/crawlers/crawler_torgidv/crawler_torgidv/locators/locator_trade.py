class LocatorTrade:
    trading_link_loc = '//a[@class="btn btn-green"]/@href'

    trading_type_loc = '//td[contains(normalize-space(text()), "Тип торгов")]/following-sibling::td/text()'
    trading_form_loc = '//td[contains(normalize-space(text()), "Вид предложения о цене")]/following-sibling::td/text()'
    trading_org_sro_loc = '//td[contains(normalize-space(text()), "Наименование СРО")]/following-sibling::td/text()'
    trading_org_fio_loc = (
        '//td[contains(normalize-space(text()), "ФИО")]/following-sibling::td/text()'
    )
    trading_org_fio_loc_2 = (
        '//td[contains(normalize-space(text()), "Ф.И.О.")]/following-sibling::td/text()'
    )
    trading_org_inn_loc = '//h2[normalize-space(text())="Организатор торгов"]/following::td[contains(text(), "ИНН") and following::h2[contains(text(), "Информация о торгах")]]/following-sibling::td/text()'
    phone_org_loc = '//h2[normalize-space(text())="Организатор торгов"]/following::td[contains(text(), "Телефон") and following::h2[contains(text(), "Информация о торгах")]]/following-sibling::td/text()'
    email_org_loc = '//h2[normalize-space(text())="Организатор торгов"]/following::td[contains(text(), "E-mail") and following::h2[contains(text(), "Информация о торгах")]]/following-sibling::td/text()'
    region_loc = (
        '//td[contains(normalize-space(text()), "Регион")]/following-sibling::td/text()'
    )
    sud_loc = '//td[contains(normalize-space(text()), "Наименование суда")]/following-sibling::td/text()'
    msg_number_loc = '//td[contains(text(), "ЕФРСБ")]/following-sibling::td/text()'
    case_number_loc = (
        '//td[contains(text(), "Номер дела")]/following-sibling::td/text()'
    )
    start_date_requests_loc = '//td[contains(normalize-space(text()), "Дата и время начала подачи заявок")]/following-sibling::td/text()'
    end_date_requests_loc = '//td[contains(normalize-space(text()), "Дата и время окончания подачи заявок")]/following-sibling::td/text()'
    start_date_trading_loc = '//td[contains(normalize-space(text()), "Дата и время начала торгов")]/following-sibling::td/text()'
    end_date_trading_loc = '//td[contains(normalize-space(text()), "Дата и время окончания торгов")]/following-sibling::td/text()'
    files_loc = (
        '//h2[contains(text(), "Документы")]/following::table[1]//a[@download]/@href'
    )

    lots_loc = '//h2[contains(text(), "Лоты")]/following::table[1]//a/@href'

    debitor_inn_loc = '//td[contains(text(), "Сведения о собственнике имущества")]/ancestor::table[1]//td[contains(normalize-space(text()), "ИНН")]/following-sibling::td/text()'
    arbit_last_name_loc = '//td[contains(text(), "Сведения об арбитражном управляющем")]/ancestor::table[1]//td[contains(normalize-space(text()), "Фамилия")]/following-sibling::td/text()'
    arbit_first_name_loc = '//td[contains(text(), "Сведения об арбитражном управляющем")]/ancestor::table[1]//td[contains(normalize-space(text()), "Имя")]/following-sibling::td/text()'
    arbit_middle_name_loc = '//td[contains(text(), "Сведения об арбитражном управляющем")]/ancestor::table[1]//td[contains(normalize-space(text()), "Отчество")]/following-sibling::td/text()'
    arbit_manager_inn_loc = '//td[contains(text(), "Сведения об арбитражном управляющем")]/ancestor::table[1]//td[contains(normalize-space(text()), "ИНН")]/following-sibling::td/text()'
    arbit_manager_org_loc = '//td[contains(text(), "Сведения об арбитражном управляющем")]/ancestor::table[1]//td[contains(normalize-space(text()), "Наименование саморегулируемой организации")]/following-sibling::td/text()'
    status_loc = '//td[contains(normalize-space(text()), "Статус торгов")]/following-sibling::td/text()'
    lot_number = '//td[contains(normalize-space(text()), "Код торгов")]/following-sibling::td/text()'
    short_name_loc = '//td[contains(normalize-space(text()), "Наименование лота")]/following-sibling::td/text()'
    lot_info_loc = '//td[contains(normalize-space(text()), "Сведения об имуществе")]/following-sibling::td/text()'
    property_information_loc = '//td[contains(normalize-space(text()), "Порядок ознакомления с имуществом")]/following-sibling::td/text()'
    start_price_loc = '//td[contains(normalize-space(text()), "Начальная цена продажи")]/following-sibling::td/text()'
    step_price_loc = '//td[contains(normalize-space(text()), "Величина повышения начальной цены продажи")]/following-sibling::td/text()'

    categories_loc = '//td[contains(normalize-space(text()), "Классификатор имущества для")]/following-sibling::td/text()'
