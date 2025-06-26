class GeneralInfoLocator:
    trading_number_loc = 'normalize-space(//div[@class="header-block-title"]/text())'

    # 5 div with trading type and traing form
    trading_type_loc = '//label[contains(.,"Вид торгов")]/ancestor::div[1]'

    # 6 organizator div
    organizer_div_loc = '//label[contains(.,"Организатор")]/ancestor::div[1]'

    # 16 - status
    status_loc = 'normalize-space(//div[@class="header-block-state"]/text())'

    # 23-24
    date_request_period_auction = (
        '//label[contains(.,"ериод приема заявок")]/ancestor::div[1]'
    )

    # 25
    start_date_trading_auc_loc = (
        '//label[contains(.,"ата и время начала аукцион")]/ancestor::div[1]'
    )

    # 26
    end_date_trading_auc_loc = (
        '//label[contains(.,"ата и время завершени")]/ancestor::div[1]'
    )
