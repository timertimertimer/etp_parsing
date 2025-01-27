###_BASIC_INFO_###
following_td = '/following::td[1]'
pagination_button_loc = '//a[@class="pagination__nav-btn pagination__nav-btn_active pagination__link"][last()]'
# status_take from lot grid on serp__###
status_loc = '//a[contains(@href,"{}")]/ancestor::div[1]/ancestor::div[1]//div[' \
             '@class="marketplace-unit__info__proposal"][1]//span[1]'

trading_form_from_serp = '//a[contains(@href,"{}")]/ancestor::div[1]/ancestor::div[1]//div[' \
                        '@class="marketplace-unit__info__name"][1]//span[1]'

extra_short_name = '//td[contains(text(),"Предмет")]/following::td[1]'
# _oazf
oazf_lots_loc = '.lots_list'



#####__OFFER__#######
#_documents_offer_#
# doc_lot_num_loc -> number of files relates to lots; doc_proc_num_loc -> number of files relates to procedure page
doc_proc_num_loc = '//a[@href[contains(.,"proc")]]/ancestor::li//span[@title]/text()'
doc_lot_num_loc = '//a[@href[contains(.,"{}")]]/ancestor::li//span[@title]/text()'




doc_link_loc = 'a[href *= "/procedure/documentation"]'
div_info_lot_offer = '//div[contains(@class,"panel panel-default panel-striped lot_head")]'
# //div[contains(@id, "209296")]/ancestor::div[contains(@class,"lot_head")]



