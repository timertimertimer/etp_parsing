# -*- coding: utf-8 -*-
class TradeLocator:
    trading_number_loc = '//div[@class="lot-regnumber"]'
    trading_type_loc = '//div[normalize-space(text())="Форма проведения торгов и подачи предложений"]/following-sibling::div[1]'
    trading_organ_loc = '//div[normalize-space(text())="Организатор торгов"]/following::div[normalize-space(text())="Наименование"]/following-sibling::div'
    trading_org_inn_loc = '//div[normalize-space(text())="Организатор торгов"]/following::div[normalize-space(text())="ИНН"]/following-sibling::div'
    email_organ_loc = '(//div[normalize-space(text())="Организатор торгов"]/following::div[normalize-space(text())="Адрес электронной почты"]/following-sibling::div[1])[1]'
    phone_organ_loc = '//div[normalize-space(text())="Организатор торгов"]/following::div[normalize-space(text())="Телефон"]/following-sibling::div[1]'
    msg_number_loc = '//div[normalize-space(text())="Идентификационный номер торгов на ЕФРСБ"]/following-sibling::div[1]'
    case_number_loc = '//div[normalize-space(text())="Номер дела о банкротстве"]/following-sibling::div[1]'
    debitor_inn_loc = '//div[normalize-space(text())="Сведения о должнике"]/following::div[normalize-space(text())="ИНН"]/following-sibling::div[1]'

    count_lots_loc = '//div[@class="generalview-container"]'

    arbitr_manag_loc = '//div[normalize-space(text())="Арбитражный управляющий"]/following::div[normalize-space(text())="ФИО"]/following-sibling::div[1]'
    finance_manag_loc = '//div[normalize-space(text())="Финансовый управляющий"]/following::div[normalize-space(text())="ФИО"]/following-sibling::div[1]'
    arbitr_inn_loc = '//div[normalize-space(text())="Арбитражный управляющий"]/following::div[normalize-space(text())="ИНН"]/following-sibling::div[1]'
    finance_inn_loc = '//div[normalize-space(text())="Финансовый управляющий"]/following::div[normalize-space(text())="ИНН"]/following-sibling::div[1]'
    arbitr_org_loc = '//div[normalize-space(text())="Арбитражный управляющий"]/following::div[normalize-space(text())="Название саморегулируемой организации"]/following-sibling::div[1]'
    finance_org_loc = '//div[normalize-space(text())="Финансовый управляющий"]/following::div[normalize-space(text())="Название саморегулируемой организации"]/following-sibling::div[1]'

    lot_title = '//h2[@class="lot-title"]'
    status_loc = '//div[normalize-space(text())= "Информация о торгах"]/following::div[normalize-space(text())="Статус"]/following-sibling::div/text()'
    short_name_loc = '//div[@class="generalview-container" and @data-lotnumber="{}"]//div[normalize-space(text())="Сведения по лоту"]/following-sibling::div//div[normalize-space(text())="Наименование лота"]/following-sibling::div'
    lot_info_loc = '//div[@class="generalview-container" and @data-lotnumber="{}"]//div[normalize-space(text())="Сведения по лоту"]/following-sibling::div//div[contains(text(), "Cведения об имуществе")]/following-sibling::div'
    region_loc = '//div[@class="generalview-container"]//div[normalize-space(text())="Сведения по лоту"]/following-sibling::div//div[contains(text(), "Регион местонахождения имущества")]/following-sibling::div'
    sud_loc = '//div[normalize-space(text())="Сведения о должнике"]/following::div[normalize-space(text())="Наименование арбитражного суда"]/following-sibling::div[1]'
    property_info_loc = '//div[normalize-space(text())="Контакты"]/following::div[normalize-space(text())="Порядок ознакомления с имуществом должника"]/following-sibling::div'

    start_price_loc = '//div[@class="generalview-container" and @data-lotnumber="{}"]//div[normalize-space(text())="Сведения по лоту"]/following-sibling::div//div[normalize-space(text())="Начальная цена продажи имущества, руб."]/following-sibling::div'
    period_table_loc = '//div[@class="generalview-container" and @data-lotnumber="{}"]//div[normalize-space(text())="Сведения по лоту"]/following-sibling::div//div[normalize-space(text())="График снижения цены"]//following-sibling::div//table'

    file_lot_link_loc = '//div[@class="generalview-container" and @data-lotnumber="{}"]//div[normalize-space(text())="Сведения по лоту"]/following-sibling::div//div[@class="sfi-info"]//a'
    general_files_loc = '//div[normalize-space(text())="Информация о торгах"]/following::div[@class="sfi-info"]//a'
    image_loc = '//div[@class="gallery-container"]//img'


class LocatorAuction:
    step_price_loc = '//div[@class="generalview-container" and @data-lotnumber="{}"]//div[normalize-space(text())="Величина повышения начальной цены"]/following-sibling::div'

    start_date_request_loc = '//div[normalize-space(text())="Информация о торгах"]/following::div[normalize-space(text())="Начало предоставления заявок на участие"]/following-sibling::div'
    end_date_request_loc = '//div[normalize-space(text())="Информация о торгах"]/following::div[normalize-space(text())="Окончание предоставления заявок на участие"]/following-sibling::div'
    start_date_trading_loc = '//div[normalize-space(text())="Информация о торгах"]/following::div[normalize-space(text())="Начало подачи предложений о цене имущества"]/following-sibling::div'
    end_date_trading_loc = '//div[normalize-space(text())="Информация о торгах"]/following::div[normalize-space(text())="Дата и время подведения результатов торгов"]/following-sibling::div'
