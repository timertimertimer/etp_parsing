class CompetLocator:
    msg_number_loc = '//legend[contains(., "Информация о конкурсе №")]/ancestor::fieldset//td[contains(., "омер сообщения в ЕФРСБ")]//following-sibling::td[1]'
    trading_num_loc = '//legend[contains(., "Информация о конкурсе №")]'

    lot_table = '//legend[contains(., "Лоты конкурса")]/ancestor::fieldset'
    property_info_loc = '//legend[contains(., "нформация о конкурсе") or contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "орядок ознакомления с имущество")]//following-sibling::td[1]'

    trading_form_loc = '//legend[contains(., "нформация о конкурсе")]/ancestor::fieldset//td[contains(., "Форма торга по составу участников:")]/following-sibling::td[1]'

    start_date_request_loc = '//legend[contains(., "нформация о конкурсе №")]/ancestor::fieldset//td[contains(., "ата начала представления заявок на учас")]//following-sibling::td[1]'
    end_date_request_loc = '//legend[contains(., "нформация о конкурсе №")]/ancestor::fieldset//td[contains(., "ата окончания представления заявок на учас")]//following-sibling::td[1]'
    start_date_trading_loc = '//legend[contains(., "нформация о конкурсе №")]/ancestor::fieldset//td[contains(., "Дата проведения")]//following-sibling::td[1]'
    extra_start_date_trading = '//legend[contains(., "нформация о конкурсе №")]/ancestor::fieldset//td[contains(., "ата подведения результатов торго")]//following-sibling::td[1]'
    start_date_trading_utender_loc = '//legend[contains(., "одведение результатов торгов")]/ancestor::fieldset//td[contains(., "ата:")]//following-sibling::td[1]'
