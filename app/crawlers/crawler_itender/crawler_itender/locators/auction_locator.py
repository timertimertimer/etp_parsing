class AuctionLocator:
    pagination_on_page = 'normalize-space(.//td[@class="pager"]//a/text())'
    # if first download not 1st page
    # extra pagination_on_page
    pagination_reverse_loc = 'normalize-space(.//td[@class="pager"]//a/text())'

    oranizer_name_loc = '//legend[contains(., "Организатор")]/ancestor::fieldset//td[contains(., "Сокращенное наименование:")]/following-sibling::td[1]'
    organizer_inn_loc = '//legend[contains(., "Организатор")]/ancestor::fieldset//td[contains(., "ИНН")]/following-sibling::td[1]'
    organizer_phone_loc = '//legend[contains(., "лицо организа")]/ancestor::fieldset//td[contains(., "елефон")]/following-sibling::td[1]'
    organizer_email_loc = '//legend[contains(., "лицо организа")]/ancestor::fieldset//td[contains(., "электронн")]/following-sibling::td[1]'

    msg_number_loc = '//legend[contains(., "нформация об аукционе")]/ancestor::fieldset//td[contains(., "омер сообщения в ЕФРСБ")]//following-sibling::td[1]'
    case_number_loc = '//legend[contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "омер дела о банкротстве")]//following-sibling::td[1]'

    debtor_inn_loc = '//legend[contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "ИНН")]//following-sibling::td[1]'
    address_loc = '//legend[contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "Регион")]//following-sibling::td[1]'
    sud_loc = '//legend[contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "Наименование арбитражного суда")]//following-sibling::td[1]'

    arbitr_name_loc = '//legend[contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "рбитражный управляющи")]//following-sibling::td[1]'
    arbitr_org_loc = '//legend[contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "именование организации арбитражных упр")]//following-sibling::td[1]'

    lot_table = '//legend[contains(., "Лоты аукциона")]/ancestor::fieldset'

    start_date_request_loc = '//legend[contains(., "нформация об аукционе")]/ancestor::fieldset//td[contains(., "ата начала представления заявок на учас")]//following-sibling::td[1]'

    end_date_request_loc = '//legend[contains(., "нформация об аукционе")]/ancestor::fieldset//td[contains(., "ата окончания представления заявок на учас")]//following-sibling::td[1]'
    start_date_trading_loc = '//legend[contains(., "нформация об аукционе")]/ancestor::fieldset//td[contains(., "Дата проведения")]//following-sibling::td[1]'
    extra_start_date_trading = '//legend[contains(., "нформация об аукционе")]/ancestor::fieldset//td[contains(., "ата подведения результатов торго")]//following-sibling::td[1]'
    start_date_trading_utender_loc = '//legend[contains(., "одведение результатов торгов")]/ancestor::fieldset//td[contains(., "ата:")]//following-sibling::td[1]'
    # auction lot page
    lot_number_loc = '//legend[contains(., "нформация о лоте №")]'

    short_name_loc = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "Наименование")]//following-sibling::td[1]'
    lot_info_loc = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "ведения об имуществе")]//following-sibling::td[1]'
    property_info_loc = '//legend[contains(., "нформация об аукционе") or contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "орядок ознакомления с имущество")]//following-sibling::td[1]'

    start_price_auc_loc = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(@class, "tdTitle") and contains(., "Начальная цена")]/following-sibling::td[1]'
    start_price_extra_auc_loc = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "Начальная цена")]//following-sibling::td[2]'

    step_price_auc_percent = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "Шаг, %")]//following-sibling::td[1]'
    step_price_auc_rub = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "Шаг, руб")]//following-sibling::td[1]'
    step_price_auc_rub_2 = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "Шаг:")]//following-sibling::td[1]'

    categories_loc = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "Классификатор ЕФРСБ")]//following-sibling::td[1]'

    status_loc = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "Статус")]//following-sibling::td[1]'
    status2_loc = '//legend[contains(., "нформация о лоте №")]/ancestor::fieldset//td[contains(., "Статус")]//following-sibling::td[1]/span'
