class Locator:
    trading_type = '//td[contains(text(), "Тип торгов")]/following-sibling::td[1]'
    trading_number = (
        '//span[contains(text(),"дентификационный номер")]/following::text()[1]'
    )
    trading_org = (
        '//th[contains(text(), "нформация об организаторе")]/ancestor::table[1]'
    )
    trading_org2 = '//th[contains(text(), "Контактное лицо организатора торгов")]/ancestor::table[1]'
    trade_info = (
        '//th[contains(text(), "нформация о проведении торгов")]/ancestor::table[1]'
    )
    extra_loc_debtor = 'normalize-space(//th[contains(., "о должнике")]/ancestor::table[1]//td[contains(., "ИНН")]/following-sibling::td[1]/text())'
    debtor_info = '//th[contains(text(), "нформация о должнике")]/ancestor::table[1]'
    arbitr_info = '//th[contains(text(), "нформация об арбитражном управляющем")]/ancestor::table[1]'
    dates_trading = (
        '//th[contains(text(), "нформация о ходе торгов")]/ancestor::table[1]'
    )
