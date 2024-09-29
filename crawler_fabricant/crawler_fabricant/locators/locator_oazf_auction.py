class LocatorOazfAuction:
    following_td = '/following-sibling::td[1]'
    trading_number = '//a[@name="{}"]/following-sibling::div//td[@class="lot_title"]'

    msg_number_loc = '//td[contains(text(),"сообщения на ЕФРСБ")]/following::td[1]'
    case_number_loc = '//td[contains(text(),"Номер дела о")]/following::td[1]'

    trading_org_loc = '//td[contains(text(),"Организатор торго")]' + following_td
    trading_org_inn = '//tr/td[contains(text(), "ИНН")]/following-sibling::td[1]'
    organiz_phone_loc = '//tr/td[contains(text(), "елефоны и факсы организаци")]//following::tr[1]/td[last()]'

    debitor_inn = '//tr/td[contains(text(), "ИНН должника")]/following-sibling::td[1]'

    arbitr_manager_loc = '//td[contains(text(),"ФИО арбитражного")]/following::td[1]'
    arbitr_org_loc = '//td[contains(text(),"аименование СРО, членом которой является арбит")]/following::td[1]'
    arbitr_inn_loc = '//td[contains(text(),"ИНН арбитражного")]/following::td[1]'

    ####__LOT__INFO__####
    short_name_loc = '//a[@name="{}"]/following-sibling::div//td[contains(text(), "арактеристики, описание предмета")]//following-sibling::td[1]'
    property_information_loc = '//a[@name="{}"]/following-sibling::div//td[contains(text(), "Порядок ознакомления с имуществом")]//following-sibling::td[1]'

    start_date_request_auc_loc = '//a[@name="{}"]/following-sibling::div//td[contains(text(), "ата и время начала приема заявок")]//following-sibling::td[1]'
    end_date_request_auc_loc = '//a[@name="{}"]/following-sibling::div//td[contains(text(), "ата и время окончания приема заяво")]//following-sibling::td[1]'
    start_date_trading_loc = '//a[@name="{}"]/following-sibling::div//td[contains(text(), "ата и время окончания приема предложений")]//following-sibling::td[1]'
    end_date_trading_loc = '//a[@name="{}"]/following-sibling::div//td[contains(text(), "ата и время подведения результатов торг")]//following-sibling::td[1]'

    start_price_loc = '//a[@name="{}"]/following-sibling::div//td[contains(text(), "ачальная цена продажи имуществ")]//following-sibling::td[1]'

    # _documentation
    link_to_doc_page_loc = '//a[text()="Документация по торгам"]'
    doc_table_oazf_lot_loc = '//a[@name="{}"]/ancestor::div//table'


# b = LocatorOazfAuction
# print(b.short_name_loc)

