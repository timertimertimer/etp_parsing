class SerpListLocator:
    """locators of the page with output after post request"""
    current_page_loc = '//tr[@class="pager"]//span[1]/text()'
    next_page_loc = '//tr[@class="pager"]//span[1]/following::td[1]/a'

    pagination_text_loc = '//table[@id="ctl00_cphBody_PaggingAdvInfo1_tblPaggingAdvInfo"]//tr//td[contains(., "Показано с")]'

    # for bs4
    id_text_num_msg = 'ctl00_cphBody_PaggingAdvInfo1_tblPaggingAdvInfo'
    text_how_many_msg = "Показано с"
