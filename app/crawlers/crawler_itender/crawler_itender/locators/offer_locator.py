class OfferLocator:
    trading_num_loc = '//legend[contains(., "Информация о публичном предложении №")]'
    msg_number_loc = '//legend[contains(., "Информация о публичном предложении №")]/ancestor::fieldset//td[contains(., "омер сообщения в ЕФРСБ")]//following-sibling::td[1]'

    lot_table = (
        '//legend[contains(., "Лоты публичного предложения")]/ancestor::fieldset'
    )
    property_info_loc = '//legend[contains(., "нформация о публичном предложении") or contains(., "нформация о должнике")]/ancestor::fieldset//td[contains(., "орядок ознакомления с имущество")]//following-sibling::td[1]'

    trading_form_loc = '//legend[contains(., "нформация о публичном предложении")]/ancestor::fieldset//td[contains(., "Форма торга по составу участников:")]/following-sibling::td[1]'
    trading_form_loc_2 = '//legend[contains(., "нформация о публичном предложении")]/ancestor::fieldset//td[contains(., "Форма представления предложений о цене:")]/following-sibling::td[1]'

    period_table_loc = '//td[contains(text(), "Дата начала приема заявок на интервале")]/ancestor::table[1]'

    documents = '//legend[contains(., "Документы")]/ancestor::fieldset//a[contains(@href, "/public/attachments/file/")]'
