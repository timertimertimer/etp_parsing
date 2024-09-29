class TradingLocators:
    organizer_link_loc = '//tr//td[1][contains(text(), "Организатор")]/following-sibling::td[1]'

    case_number = '//tr//td[1][contains(text(), "омер дела о банкротстве")]/following-sibling::td[1]'
    msg_number = '//tr//td[1][contains(text(), "омер сообщения в ЕФРСБ")]/following-sibling::td[1]'
    debtor_block_loc = '//tr//td[1][contains(text(), "анные должника")]/following-sibling::td[1]'

    arbitr_block_loc = '//tr//td[1][contains(text(), "анные арбитражного управляющег")]/following-sibling::td[1]'

    property_info_loc = '//tr//td[1][contains(text(), "ополнительная информация о процедуре")]/following-sibling::td[1]'
    # auction
    start_date_request_loc = '//tr//td[1][contains(text(), "ата начала подачи заявок")]/following-sibling::td[1]'
    end_date_request_loc = '//tr//td[1][contains(text(), "ата окончания подачи заявок")]/following-sibling::td[1]'
    start_date_trading_loc = '//tr//td[1][contains(text(), "ата начала аукциона")]/following-sibling::td[1]'
