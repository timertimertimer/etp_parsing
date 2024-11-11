class LocatorLot:
    lot_number_loc = 'normalize-space(//div[@class="panel-heading clearfix"])'
    short_name_loc = 'normalize-space(//div[contains(text(),"редмет договора (наименование реализуемого имуще")]/following-sibling::div[1])'
    short_name_loc2 = 'normalize-space(//div[contains(text(),"редмет договора")]/following-sibling::div[1])'
    property_info_loc = 'normalize-space(//div[contains(text(),"орядок ознакомления с имущество")]/following-sibling::div[1])'

    # NEW AUCTION
    start_request_auction = 'normalize-space(//div[contains(text(), "Дата и время начала приема")]/following-sibling::div[1])'  # Дата и время начала приема заявок
    end_request_auction = 'normalize-space(//div[contains(text(), "Дата и время окончания приема заявок")]/following-sibling::div[1])'  # Дата и время окончания приема заявок
    start_trading_auction = 'normalize-space(//div[contains(text(), "Дата и время начала аукциона")]/following-sibling::div[1])'  # Дата и время начала аукциона
    end_date_trading_auc = 'normalize-space(//div[contains(text(), "Дата и время подведения итогов")]/following-sibling::div[1])'  # Дата и время подведения итогов
    start_price_auc = 'normalize-space(//div[contains(text(), "Начальная цена предмета договора")]/following-sibling::div[1])'  # Начальная цена предмета договора
    step_price_auc = 'normalize-space(//div[contains(text(), "Шаг аукциона")]/following-sibling::div[1])'  # Шаг аукциона