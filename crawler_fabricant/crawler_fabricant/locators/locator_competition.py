class LocatorCompetition:
    trade_form = '//td[contains(text(),"Форма конкурса")]/following::td[1]/text()'

    trading_org_td_loc = '//td[contains(text(),"Организатор процедуры")]/following-sibling::td[1]'

    msg_num_loc = '//td[contains(text(),"сообщения на ЕФРСБ")]/following-sibling::td[1]'
    case_number_loc = '//td[contains(text(),"дела о банкротстве")]/following-sibling::td[1]'

    debtor_inn_loc = '//td[contains(text(),"Должник")]/following-sibling::td[1]'

    arbitr_manager_loc = '//tr//td[contains(text(),"Арбитражный управляющий")][1]/following-sibling::td[1]'
    arbitr_org_loc = '//tr//td[contains(text(),"СРО, членом которой является арбитражный")][1]/following-sibling::td[1]'

    start_date_requests = '//tr//td[contains(text(),"ата публикации в МТС")][1]/following-sibling::td[1]'
    end_date_requests = '//tr//td[contains(text(),"ата окончания приема конкурсных")][1]/following-sibling::td[1]'
    start_date_trading = '//tr//td[contains(text(),"ата завершения процедур")][1]/following-sibling::td[1]'

    # _lot_info
    short_name_loc = '//td[contains(text(),"Предмет")]/following::td[1]'
    start_price_comp_loc = '//td[contains(text(),"Начальная цена")]/following::td[1]'
    property_information_loc = '//tr//td[contains(text(),"орядок ознакомления с имуществом")][1]/following-sibling::td[1]'