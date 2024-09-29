###_BASIC_INFO_###
LIST_OF_LINKS_TO_TRADING = '//tr[contains(@onclick,"/Trade/AnounsmentDetails/")]'
status_loc = '//tr[contains(@onclick,"{}")]//td[last()]/text()'
# _ status -----   //tr[contains(@onclick,"/Trade/AnounsmentDetails/")]//td[last()]
periods_offer = '//td[contains(., "Периоды снижения цены")]/following::table[contains(.,"Задаток")]'
all_files = '//td/img[contains(@src,"/Content/img/")]/following::td[1]'
tr_files = '//td//img[contains(@src,"/Content/img/icons/")]/ancestor::tr'
pagination = '//div[@id="paginator"]/a[last()]'

##########_________INFO________ABOUT_________ORGANIZATOR______#########
trade_org_info = None
# //td[contains(., "ИНН")]/ancestor::td//td[contains(., "ИНН")]/following-sibling::td[2]
last_name_org = '//td[contains(., "ведения об организаторе торго")]/ancestor::td//td[contains(., "ведения об ' \
                'организаторе торго")]/following::td[contains(.,"амилия")]/following-sibling::td[2]/text()'
inn_org_loc = '//td[contains(., "ведения об организаторе торго")]/ancestor::td//td[contains(., "ведения об ' \
              'организаторе торго")]/following::td[contains(.,"ИНН")]/following-sibling::td[2]/text()'

first_name_org = '//td[contains(., "ведения об организаторе торго")]/ancestor::td//td[contains(., "ведения об ' \
                 'организаторе торго")]/following::td[contains(.,"Имя")]/following-sibling::td[2]/text()'
middle_name_org = '//td[contains(., "ведения об организаторе торго")]/ancestor::td//td[contains(., "ведения об ' \
                  'организаторе торго")]/following::td[contains(.,"Отчество")]/following-sibling::td[2]/text()'

email_org_loc = '//td[contains(., "ведения об организаторе торго")]/ancestor::td//td[contains(., "ведения об ' \
                'организаторе торго")]/following::td[contains(.,"дрес электронной почты")]/following-sibling::td[2]/a/text()'

phone_org_loc = '//td[contains(., "ведения об организаторе торго")]/ancestor::td//td[contains(., "ведения об ' \
                'организаторе торго")]/following::td[contains(.,"омер контактного телефон")]/following-sibling::td[2]/text()'

organization_name = '//td[contains(., "ведения об организаторе торго")]/ancestor::td//td[contains(., "ведения об ' \
                    'организаторе торго")]/following::td[contains(.,"Полное наименование")]/following-sibling::td[2]/text()'

organization_name_short = '//td[contains(., "ведения об организаторе торго")]/ancestor::td//td[contains(., "ведения об ' \
                          'организаторе торго")]/following::td[contains(.,"Краткое наименование")]/following-sibling::td[2]/text()'

#########______DEBITOR_____________INFO###########
deb_info = '//td[contains(., "ведения о должнике")]/ancestor::td//td[contains(., "ведения о должнике")]'
debitor_inn = deb_info + \
    '/following::td[contains(.,"ИНН")]/following-sibling::td[2]/text()'
info_trade = None
msg_number = '//td[contains(., "ведения о процедуре торгов")]/ancestor::td//td[contains(., "ведения о процедуре ' \
             'торгов")]/following::td[contains(.,"омер сообщения «Объявление о проведении торгов» опубликованного")]/following-sibling::td[2]/text() '
case_number_loc = '//td[contains(., "ведения о процедуре торго")]/ancestor::td//td[contains(., "ведения о процедуре ' \
    'торго")]/following::td[contains(.,"омер дела о банкротстве")]/following-sibling::td[2]/text()'
trading_type_loc = '//td[contains(., "ведения о процедуре торго")]/ancestor::td//td[contains(., "ведения о процедуре ' \
    'торго")]/following::td[contains(.,"Форма проведения открытых торгов")]/following-sibling::td[2]/text()'

# ________ARBITR________INFO____________________
table_arbitr = None
arbitr_last_name_loc = '//td[contains(., "ведения об арбитражном управляющем")]/ancestor::td//td[contains(., ' \
                       '"ведения об арбитражном управляющем")]/following::td[contains(.,' \
                       '"амилия")]/following-sibling::td[2]/text() '

arbitr_first_name_loc = '//td[contains(., "ведения об арбитражном управляющем")]/ancestor::td//td[contains(., ' \
                        '"ведения об арбитражном управляющем")]/following::td[contains(.,' \
                        '"Имя")]/following-sibling::td[2]/text() '
arbitr_middl_name_loc = '//td[contains(., "ведения об арбитражном управляющем")]/ancestor::td//td[contains(., ' \
                        '"ведения об ' \
                        'арбитражном управляющем")]/following::td[contains(.,"Отчество")]/following-sibling::td[' \
                        '2]/text() '

arb_man_inn = '//td[contains(., "ведения об арбитражном управляющем")]/ancestor::td//td[contains(., ' \
              '"ведения об арбитражном управляющем")]/following::td[contains(.,' \
              '"ИНН")]/following-sibling::td[2]/text() '
arbit_manager_org_loc = '//td[contains(., "ведения об арбитражном управляющем")]/ancestor::td//td[contains(., ' \
                        '"ведения об арбитражном управляющем")]/following::td[contains(.,' \
                        '"Наименование СРО")]/following-sibling::td[2]/text() '

###_WORKING_WITH_DATES_###
# _info_has_more_influence_to_auction_#
start_date_request_loc = '//td[contains(., "ата и время начала представления заявок на участие")]/ancestor::td//td[' \
                         'contains(., "ата и время начала представления заявок на участие")]/following-sibling::td[2]/text()'
end_date_requests_loc = '//td[contains(., "ата и время окончания представления заявок на участие")]/ancestor::td//td[' \
                        'contains(., "ата и время окончания представления заявок на участие")]/following-sibling::td[2]/text()'
start_date_trading_loc = '//td[contains(., "ата и время начала проведения торго")]/ancestor::td//td[' \
                         'contains(., "ата и время начала проведения торго")]/following-sibling::td[2]/text()'
end_date_trading_loc = '//td[contains(., "ата и время подведения результато")]/ancestor::td//td[' \
                       'contains(., "ата и время подведения результато")]/following-sibling::td[2]/text()'

###_WORKING_WITH_LOTS_###
all_lot_title = '//td[contains(.,"Лот")]/ancestor::td//td[@class="doc_part"][contains(.,"Лот")]/text()'
# _working_with_prices_#
lot_ancestor = '//td[contains(.,"Лот № {0}")]/ancestor::td//td[@class="doc_part"][contains(.,"Лот № {0}")]'
start_price_loc = lot_ancestor + \
    '/following::td[contains(.,"ачальная цена продажи имущества (предприятия) должника")]/following-sibling::td[2]/text()'
step_price_loc = lot_ancestor + '/following::td[contains(.,"еличина повышения начальной цены продажи имущества (' \
                                'предприятия), «шаг аукциона»")]/following-sibling::td[2]/text() '

td_short_name = 'ведения об имуществе должника (состав, характеристики, описание, порядок ознакомления с имущество'
following_sibling = '/following-sibling::td[2]/text()'
short_name_loc = lot_ancestor + \
    f'/following::td[contains(.,"{td_short_name}")]' + following_sibling


#_working_with_offer_periods_#
period_table_data = lot_ancestor + \
    '/following::td[contains(., "Периоды снижения цены")]/following::table[contains(.,"Задаток")]//tr//text()'
