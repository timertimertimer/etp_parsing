###_BASIC_INFO_###
follow_sibling = '/following::td[1]/text()'

TABLE_LIST_OF_LINKS_TO_TRADE = 'div.news-list tr a'
##########_________INFO________ABOUT_________ORGANIZATOR______#########
table_trade_organizator = '//fieldset[contains(.,"Организатор торгов")]'
td_organizator_name = '//fieldset[contains(.,"Организатор торгов")]//td[contains(text(),"онтактное лиц")]'
td_org_inn = '//fieldset[contains(.,"Организатор торгов")]//td[contains(text(),"ИНН")]'
td_email_org = '//fieldset[contains(.,"Организатор торгов")]//td[contains(text(),"дрес электронной почты")]'
td_phone_org = '//fieldset[contains(.,"Организатор торгов")]//td[contains(text(),"онтактный телефо")]'
organizator_name_loc = td_organizator_name + follow_sibling
td_naimenovanie = '//fieldset[contains(.,"Организатор торгов")]//td[contains(text(),"Наименование")]'
organizator_loc = td_naimenovanie + follow_sibling

organiz_inn_loc = td_org_inn + follow_sibling
organiz_email_loc = td_email_org + follow_sibling
organiz_phone_loc = td_phone_org + follow_sibling
#########______DEBITOR_____________INFO###########
td_debitor_inn = '//fieldset[contains(.,"ведения о должнике")]//td[contains(text(),"ИНН")]'
debit_inn_loc = td_debitor_inn + follow_sibling
###_ARBITR_INFO_###
td_arbitr_name = '//fieldset[contains(.,"ведения об арбитражном управляюще")]//td[contains(text(),"амилия Имя Отчеств")]'
td_arbitr_inn = '//fieldset[contains(.,"ведения об арбитражном управляюще")]//td[contains(text(),"ИНН")]'
td_arbitr_org = '//fieldset[contains(.,"ведения об арбитражном управляюще")]//td[contains(text(),"Наименование ' \
                'саморегулируемой организации")] '
arbitr_manager_loc = td_arbitr_name + follow_sibling
arbitr_inn_loc = td_arbitr_inn + follow_sibling  # None
arbitr_org_loc = td_arbitr_org + follow_sibling


td_msg_num = '//fieldset[contains(.,"Сведения о торгах")]//td[contains(text(),"Номер сообщения в ЕФРСБ")]'
msg_number_loc = td_msg_num + follow_sibling
td_trading_num = '//fieldset[contains(.,"Сведения о торгах")]//td[contains(text(),"Номер торгов")]'
trading_num_loc = td_trading_num + follow_sibling
td_trading_form = '//fieldset[contains(.,"Сведения о торгах")]//td[contains(text(),"Форма торгов")]'
trading_form_loc = td_trading_form + follow_sibling


td_case_number = '//fieldset[contains(.,"ведения дела о банкротств")]//td[contains(text(),"омер дела о банкротстве")]'
case_number_loc = td_case_number + follow_sibling

td_extra_case_number = '//fieldset[contains(.,"ведения дела о банкротств")]//td[contains(text(),"Основание для торгов")]'
extra_case_num_loc = td_extra_case_number + follow_sibling

td_property_info = '//fieldset[contains(.,"Сведения о торгах")]//td[contains(text(),"орядок ознакомления с имущество")]'
property_info_loc = td_property_info + follow_sibling

###_WORKING_WITH_DATES_AUCTION_###
td_start_request = '//fieldset[contains(.,"Сведения о торгах")]//td[contains(text(),"ата и время начала приема заяво")]'
td_end_request = '//fieldset[contains(.,"Сведения о торгах")]//td[contains(text(),"ата и время окончания приема ' \
    'заяво")] '
td_start_trade = '//fieldset[contains(.,"Сведения о торгах")]//td[contains(text(),"ата и время начала предложений о ' \
    'цене имуществ")] '
td_extra_date_trading_auc = '//fieldset[contains(.,"Сведения о торгах")]//td[contains(text(),"ата и время подведения итого")]'
extra_start_tading_auc_loc = td_extra_date_trading_auc + follow_sibling

start_request_loc = td_start_request + follow_sibling
end_request_loc = td_end_request + follow_sibling
start_trade_loc = td_start_trade + follow_sibling


###_WORKING_WITH_LOT_PAGE_###
td_status = '//fieldset[contains(.,"Сведения об имуществе")]//td[contains(text(),"Статус лота")]'
status_loc = td_status + follow_sibling

lot_number_loc = '//fieldset[contains(.,"Сведения об имуществе")]//td[text()="№ лота:"]/following::td[1]/text() | //td[' \
    'text()="Номер лота:"]/following::td[1]/text() '

td_short_name = '//fieldset[contains(.,"Сведения об имуществе")]//td[contains(text(),"аименование имущества")]'
short_name_loc = td_short_name + follow_sibling
td_lot_info = '//fieldset[contains(.,"Сведения об имуществе")]//td[contains(text(),"ведения об имуществе")]'
lot_info_loc = td_lot_info + follow_sibling

td_start_price = '//fieldset[contains(.,"Сведения об имуществе")]//td[contains(text(),"ачальная цена продажи имуществ")]'
td_step_price = '//fieldset[contains(.,"Сведения об имуществе")]//td[contains(text(),"Шаг аукциона")]'
start_price_loc = td_start_price + follow_sibling
step_price_loc = td_step_price + follow_sibling

###_WORKING_WITH_DATES_AND_PERIODS_###
period_table_loc = '//fieldset[contains(.,"Периоды")]//tbody//tr'
start_date_requesr_offer_loc = '//fieldset[contains(.,"Периоды")]//tbody//tr[1]/td[4]/text()'
end_date_requesr_offer_loc = '//fieldset[contains(.,"Периоды")]//tbody//tr[last()]/td[5]/text()'

###_WORKING_WITH_FILES_####
table_trading_files = '//a[contains(@href,"/upload/iblock/")]/ancestor::table[1]//tr'
table_lot_files = '//a[contains(@href,"/upload/iblock/")]/ancestor::table[1]//tr/td'
