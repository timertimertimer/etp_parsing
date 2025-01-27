class MsgLocator:
    """locators of message page"""
    msg_number_loc = '//td[contains(text(),"№ сообщени")]/following-sibling::td[1]'
    msg_pub_date_loc = '//table[@class="headInfo"]//td[contains(text(),"Дата публикации")]/following-sibling::td[1]'
    msg_deb_inn_loc = '//table[@class="headInfo"]//td[contains(text(),"ИНН")]/following-sibling::td[1]'
    msg_case_num_loc = '//table[@class="headInfo"]//td[contains(text(),"№ дела")]/following-sibling::td[1]'

    msg_deb_name = '//table[@class="headInfo"]//td[contains(text(),"ФИО должника")]/following-sibling::td[1]'
    msg_deb_place_add_loc = '//table[@class="headInfo"]//td[contains(text(),"Место жительства")]/following-sibling::td[1]'

    msg_deb_naimenovanie = '//table[@class="headInfo"]//td[contains(text(),"Наименование должника")]/following-sibling::td[1]'
    msg_deb_address = '//table[@class="headInfo"]//td[contains(text(),"Адрес")]/following-sibling::td[1]'

    msg_tenderring = '//table[@class="headInfo"]//td[contains(text(),"бъявление о проведении торго")]/following-sibling::td[1]'
    msg_canceled = '//table[@class="headInfo"]//td[contains(text(),"тмененное сообщение")]/following-sibling::td[1]'

    msg_change_trade_procedure = '//table[@class="headInfo"]//td[contains(text(),"Измененное сообщение")]/following-sibling::td[1]'

    files_loc = '//div[@class="files"]//a'

    # for bs4
    msg_type_class_loc = 'red_small'
