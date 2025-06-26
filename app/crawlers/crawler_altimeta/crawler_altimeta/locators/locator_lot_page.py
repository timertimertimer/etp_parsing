class LocatorLotPage:
    get_all_table = "//table"
    get_lot_table_offer = '//@id[contains(., "lotNumber")]/ancestor::table'
    lot_info_loc = '//th[contains(., "{}")]/ancestor::table//td[contains(., "ведения об имуществе (предприятии)")]'
    property_info_loc = '//th[contains(., "{}")]/ancestor::table//td[contains(., "орядок ознакомления с имуществом")]'
    start_price_loc = '//th[contains(., "{}")]/ancestor::table//td[contains(., "ачальная цена продажи имуществ")]'
    step_price_loc = '//th[contains(., "{}")]/ancestor::table//td[contains(., "повышения начальной цен")]'

    pagination = '//span[@class="paginatorSelectedPage"]//following::a/text()'
