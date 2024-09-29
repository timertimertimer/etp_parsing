#! -*- coding: utf-8 -*-

###_BASIC__INFO_###
pagination_active = '//ul[@class="pagination"]//li[@class="active"]/a/text()'
last_page_loc = '//nav[@class="pagnav"]//li[last()]//a/text()'
foll_sibling = '/following::td[1]/text()'
LINKS_to_TRADING_pages_loc = '//tr[contains(@onclick,"/trade_view.php?trade_nid=")]'
trading_number_loc ='normalize-space(//span[contains(text(),"дентификационный номер")]/following::text()[1])'
trading_form_loc = 'normalize-space(//td[contains(text(), "Тип торгов")]' + foll_sibling +')'
###_org_info_###
td_fio_org = 'normalize-space(//th[contains(text(),"Контактное лицо организатора торгов")]/following::td[contains(' \
             'text(),"ФИО")][1] '
td_email_org = 'normalize-space(//th[contains(text(),"Контактное лицо организатора торгов")]/following::td[contains(' \
               'text(),"E-mail")][1] '
td_phone_org = 'normalize-space(//th[contains(text(),"Контактное лицо организатора торгов")]/following::td[contains(' \
               'text(),"елефон")][1] '
fms_name_org = td_fio_org + foll_sibling + ')'
phone_org_loc = td_phone_org + foll_sibling + ')'
email_org_loc = td_email_org + foll_sibling + ')'
td_msg_number = 'normalize-space(//td[contains(text(),"мер объявления о проведении торгов на fedres")]'
msg_num_loc = td_msg_number + foll_sibling + ')'
td_case_number = 'normalize-space(//td[contains(text(),"омер дела о банкротстве")]'
case_number_loc = td_case_number + foll_sibling + ')'
##_debitor_info_###
td_deb_inn = 'normalize-space(//th[contains(text(),"Информация о должнике")]/following::td[contains(text(),"ИНН")][1]'
debitor_inn_loc = td_deb_inn + foll_sibling + ')'
###_arbitr_info_###
th_arbitr = 'normalize-space(//th[contains(text(),"Информация об арбитражном управляющем")]'
td_arbitr_last_name = '/following::td[contains(text(),"Фамилия")]'
td_arbitr_first_name = '/following::td[contains(text(),"Имя")]'
td_arbitr_middle_name = '/following::td[contains(text(),"Отчество")]'
arbit_last_name_loc = th_arbitr + td_arbitr_last_name + foll_sibling + ')'
arbitr_first_name_loc = th_arbitr + td_arbitr_first_name + foll_sibling + ')'
arbitr_middle_name_loc = th_arbitr + td_arbitr_middle_name + foll_sibling + ')'
arbitr_inn = th_arbitr + '/following::td[contains(text(),"ИНН")]' + foll_sibling + ')'
arbitr_org = th_arbitr + '/following::td[contains(text(),"Наименование СРО")]' + foll_sibling + ')'

###_WORKING_WITH_DATES_###
start_date_requests_loc = 'normalize-space(//td[contains(text(),"ата начала представления заявок на участ")]' + foll_sibling + ')'
end_date_requests_loc = 'normalize-space(//td[contains(text(),"ата окончания представления заявок на участи")]' + foll_sibling + ')'
start_date_trading_loc = 'normalize-space(//td[contains(text(),"Дата проведения")]' + foll_sibling + ')'
#_date_offer_#
start_date_request_offer_loc = '//table[@id="table_lot_{}"]//table//tr[@class[contains(.,"discount_row")]][1]/td[1]/text()'
end_date_requests_offer_loc = '//table[@id="table_lot_{}"]//table//tr[@class[contains(.,"discount_row")]][last()]/td[2]/text()'
start_date_trading_offer_loc = start_date_request_offer_loc
end_date_trading_offer_loc = end_date_requests_offer_loc
#end_date_offer_#



###_WORKING_WITH_LOTS_###
amount_lots_loc = '//span[@class="lot_title"]'
lot_number_loc = 'normalize-space(//table[@id="table_lot_{}"]//td[contains(text(),"омер лота")]' + foll_sibling + ')'
##_get_lot_number_from_th_title_#
th_lot_number = '//span[@class="lot_title"]/text()'

short_name_loc = 'normalize-space(//table[@id="table_lot_{}"]//td[contains(text(),"аименование имущества")]' + foll_sibling + ')'
lot_info_loc = 'normalize-space(//table[@id="table_lot_{}"]//td[contains(text(),"ведения об имуществе (предприятии) должника, выставляемом на торги")]' + foll_sibling + ')'
property_informationloc = 'normalize-space(//table[@id="table_lot_{}"]//td[contains(text(),"орядок ознакомления с имущест")]' + foll_sibling + ')'
#_price_#
start_price_loc = 'normalize-space(//table[@id="table_lot_{}"]//td[contains(text(),"Начальная цена")]' + foll_sibling + ')'
step_price_loc = 'normalize-space(//table[@id="table_lot_{}"]//td[contains(text(),"Шаг аукциона")]' + foll_sibling + ')'
status_loc =  'normalize-space(//table[@id="table_lot_{}"]//td[contains(.,"Статус торгов")]' + '/following::td[1]/span/text()' + ')'
###_WORKING_WITH_PERIODS_OFFER_###
table_period_loc = '//table[@id="table_lot_{}"]//table//tr[@class[contains(.,"discount_row")]]'
###-WORKING_WITH_FILES_###
files_generel_loc = '//table[contains(.,"Документы")]//a[contains(@href,"/files/")]'
all_files_loc = '//a[contains(@href,"/files/")]'
lot_files_loc = '//table[@id="table_lot_{}"]//a[contains(@href,"/files/")]'


#
# form_data_start = '//div[contains(.,"Дата начала подачи заявок")]/following-sibling::div[@class="date-from-to"]//input/following::label[1][contains(.,"от")][1]'
#
# ###_TRADING_PAGE_AUCTION_###
# foll_sibling ='/following::td[1]/text()'
# trade_type_loc = '//td[contains(.,"Вид торгов")]' + foll_sibling
# trade_form_loc = '//td[contains(.,"рма представления предложений о цен")]' + foll_sibling
# msg_num_loc = '//td[contains(.,"омер объявления о проведении торгов на сайте")]' + foll_sibling
# case_num_loc = '//td[contains(.,"омер дела о банкротстве")]' + foll_sibling
# ##########_________INFO________ABOUT_________ORGANIZATOR______#########
# trade_org_info_loc = 'normalize-space(//h3[contains(.,"нформация об организато")]'
# td_label_name = '/following::tr//following::td[contains(.,"олное наименование")]'
# org_name_loc = trade_org_info_loc + td_label_name + foll_sibling + ')'
#
# td_inn = '/following::tr//following::td[contains(.,"ИНН")]'
# inn_org = trade_org_info_loc + td_inn + foll_sibling + ')'
#
# td_email = '/following::tr//following::td[contains(.,"-mail")]'
# email_org_loc = trade_org_info_loc + td_email + foll_sibling + ')'
#
# td_phone = '/following::tr//following::td[contains(.,"онтактный телефо")]'
# phone_org_loc = trade_org_info_loc + td_phone + foll_sibling + ')'
#
# #########______DEBITOR_____________INFO###########:
# deb_info = 'normalize-space(//h3[contains(.,"нформация о должнике")]'
# td_deb_inn = '/following::tr//following::td[contains(.,"ИНН")]'
# debitor_inn = deb_info + td_deb_inn + foll_sibling +')'
#
# #############________ARBITR________INFO____________________
# arbitr_info = 'normalize-space(//h3[contains(.,"нформация об арбитражном управляю")]'
# td_arb_name = '/following::tr//following::td[contains(.,"Фамилия Имя Отчество")]'
# arbitr_name_loc = arbitr_info + td_arb_name + foll_sibling + ')'
# td_arb_inn =  '/following::tr//following::td[contains(.,"ИНН")]'
# arbitr_inn_loc = arbitr_info + td_arb_inn + foll_sibling + ')'
# td_arb_org = '/following::tr//following::td[contains(.,"Наименование СРО")]'
# arbitr_org_loc = arbitr_info + td_arb_org + foll_sibling + ')'
#
#
# ###_LOT_INFO_###
# lot_info_loc = 'normalize-space(//h3[contains(text(),"Информация о лоте")]'
# lot_number_loc = lot_info_loc + '/following::td[contains(.,"омер лота организатор")]' + foll_sibling + ')'
# short_name = lot_info_loc + '/following::td[contains(.,"писание (полное название лот")]' + foll_sibling + ')'
# property_information_loc = '//td[contains(.,"Сведения об имуществе (предприятии) должника, выставляемом на торги")]' + \
#                            foll_sibling
#
# start_price_loc = '//h3[contains(text(),"Информация о лоте")]/following::td[contains(text(),"ачальная цена")]' + foll_sibling
# step_price_loc = lot_info_loc + '/following::td[contains(text(),"Шаг аукциона")]' + foll_sibling + ')'
# step_if_bug = '//h3[contains(text(),"Информация о лоте")]/following::td[contains(text(),"Шаг аукциона")]/following::td[4]/text()'
#
# ###_WORKING_WITH_PERIODS_###
# start_date_request_loc = '//td[contains(.,"ата и время начала представления заяв")]' + foll_sibling
# end_date_request_loc = '//td[contains(.,"ата и время окончания представления заяв")]' + foll_sibling
# start_trading_loc = '//td[contains(text(),"ата и время начала торгов")]' + foll_sibling
# end_trading_loc = '//td[contains(text(),"ата и время окончания торго")]' + foll_sibling
# extra_end_trading_loc = '//td[contains(text(),"ата и время объявления результатов торгов")]' + foll_sibling
# table_period_1 = '//h3[contains(.,"График снижения цены")]/following::table[1]//tr[position()>1]'
#
#
# ###___offer__start/end___trading___#####
# lot_table_start_trade = '//h3[contains(.,"График снижения цены")]/following::table[1]//tr[position()>1][1]//td[1]/text()'
# lot_table_end_trade = '//h3[contains(.,"График снижения цены")]/following::table[1]//tr[position()>1][last()]//td[2]/text()'
