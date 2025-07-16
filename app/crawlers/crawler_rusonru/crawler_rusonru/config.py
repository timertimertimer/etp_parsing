from app.utils.config import start_date

formdata = {
    "lot_description": "",
    "trade_number": "",
    "debtor_info": "",
    "arbitr_info": "",
    "app_start_from": start_date,
    "app_start_to": "",
    "app_end_from": "",
    "app_end_to": "",
    "trade_type": "Любой",
    "trade_state": "Любой",
    "pagenum": "",
}
stop_page = 20
data_origin = {
    "ruson": "https://rus-on.ru/",
    "eltorg_commercial": "https://el-torg.com/",
    "eltorg_bankruptcy": "https://el-torg.com/",
    "nistp": "https://nistp.ru/",
    "promkonsalt": "https://promkonsalt.ru/",
    "sistematorg": "https://sistematorg.com/",
}
serp_link = {
    "ruson": "https://rus-on.ru/bankrot/trade_list.php",
    "eltorg_bankruptcy": "https://el-torg.com/bankrot/trade_list.php",
    "eltorg_commercial": "https://el-torg.com/bankrot/trade_list_commerc.php",
    "nistp": "https://nistp.ru/bankrot/trade_list.php",
    "promkonsalt": "https://promkonsalt.ru/tradelist.php",
    "sistematorg": "https://sistematorg.com/tradelist.php",
}
trade_link = {
    "ruson": "https://rus-on.ru/bankrot/trade_view.php",
    "eltorg_bankruptcy": "https://el-torg.com/bankrot/trade_view.php",
    "eltorg_commercial": "https://el-torg.com/bankrot/trade_view.php",
    "nistp": "https://nistp.ru/bankrot/trade_view.php",
    "promkonsalt": "https://promkonsalt.ru/trade_view.php",
    "sistematorg": "https://sistematorg.com/trade_view.php",
}
