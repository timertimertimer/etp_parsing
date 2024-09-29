class LocatorOffer:
    organizator_div_loc = '//div[@id="org_popup"]'

    arbitr_click_fieldset_loc = '//a[@id="formMain:clDpExpEvent4"]/ancestor::fieldset'
    arbitr_click_fieldset_text_loc = '//a[@id="formMain:clDpExpEvent4"]/text()'

    arbitr_fieldset_loc = '//div[@id="arbitr-info"]'
    arbitr_fieldset_text_loc = '//a[@id="formMain:clDpExpEvent4"]/text()'
    debitor_info_fieldset_loc = '//legend[contains(text(),"Должник")]/ancestor::fieldset'

    status_lot_loc_css = 'span[class*="status-"]'

    lot_number_css_loc = '.field-lot:nth-child(2)'
    short_name_loc = '//h1'
    extra_check_short_name_loc = '.field-lot'
    lot_info_loc = '//p[@class="field-description"][2]'
    property_info_loc = '//div[@id="excurse-info"]'

    start_price_offer_loc = '//div//p[@class="field-price"]//span[@class="price"]'
    tbody_periods_loc = '//table[contains(., "Величина изменения")]'


class LocatorAuction(LocatorOffer):
    pattern_start_end_request = r'Период приёма заявок .* (\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2}\W\d{1,2}.\d{1,2}.\d{2,4}\s\d{1,2}:\d{1,2})'
    all_files_general = 'span[id*="fileName"]'
    locator_img_lot_extra = "//span[contains(text(), '.JPG')] | //span[contains(text(), '.PNG')] | //span[contains(text(), '.jpg')] | //span[contains(text(), '.png')] | //span[contains(text(), '.jpeg')] | //span[contains(text(), '.JPEG')]"
    img_lot_locator = '//img//@src[contains(.,"resources/Temp/")]'
    id_latitude_loc = '//input[contains(@id, "formMain:addrLatitudeIdView")]'
    id_longtitude_loc = '//input[contains(@id, "formMain:addrLongitudeIdView")]'