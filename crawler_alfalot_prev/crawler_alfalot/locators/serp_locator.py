class LocatorSerp:
    pager_href = '//tr[1]/td[@class="pager"]/a'
    pager_lot_page = '//td[@class="pager"]/a'
    max_page_number_loc = './/td[@class="pager"]//span[last()]//text()'

    tr_lot_info = '//tbody/tr[@class="gridRow"]'

    trading_num_loc = '//legend[contains(., "нформация об аукционе №")]'

    trading_form_loc = '//legend[contains(., "нформация об аукционе №")]/ancestor::fieldset//td[contains(., "Форма торга по составу участников:")]/following-sibling::td[1]'
