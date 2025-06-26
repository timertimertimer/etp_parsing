class TradeLocator:
    trading_type_and_form_loc = '//div[@class="property__cards_info-item" and b[text()="Вид торгов"]]/span/text()'
    trading_org_loc = (
        '//div[@class="property__cards_subtitle" and b[text()="Организация:"]]/span'
    )
    case_number_loc = (
        '//div[@class="property__cards_subtitle" and b[text()="№ дела:"]]/span'
    )
    debtor_inn_loc = '//div[@class="property__cards_info-item" and b[text()="ИНН дебитора:"]]/span/text()'
    debtor_inn_loc2 = (
        '//div[@class="property-debtor__info_item" and b[text()="ИНН:"]]//span/text()'
    )
    address_loc = (
        '//div[@class="property__cards_subtitle" and b[text()="Регион:"]]/span/text()'
    )
    address_loc2 = (
        '//div[@class="property-debtor__info_item" and b[text()="Адрес:"]]//a/@href'
    )
    arbit_manager_loc = '//div[@class="property__cards_person-item" and span[text()="Арбитражный управляющий"]]//div[b[text()="ФИО:"]]/span'
    arbit_manager_org_loc = '//div[@class="property__cards_person-item" and span[text()="Арбитражный управляющий"]]//div[b[text()="СРО:"]]/span'
    status_loc = '//div[@class="property__cards_text-status"]/text()'
    lot_number_loc = '//div[@class="property__cards_title property__cards_title--lot"]'
    lot_info_loc = '//div[contains(@class, "property__cards_specifications") and contains(@class, "property__cards_table") and span[text()="Характеристики:"]]//div[@class="property__cards_info-item"]'
    start_date_requests_loc = '//div[@class="property__cards_info-item" and b[text()="Дата начала приёма заявок"]]/span/text()'
    end_date_requests_loc = '//div[@class="property__cards_info-item" and b[text()="Дата завершения приёма заявок"]]/span/text()'
    start_and_end_dates_trading_loc = (
        '//div[@class="property__cards_info-item" and b[text()="Дата торгов:"]]/span'
    )
    start_price_loc = '//div[@class="property__analysis_text" and p[text()="Оценочная стоимость:"]]/span/text()'
    general_files_loc = '//a[@class="property-commercial__row-link"]'
    images_carousel_loc = '//a[contains(@class, "f-carousel__slide")]'
