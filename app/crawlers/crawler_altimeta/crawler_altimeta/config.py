from app.utils.config import start_date

stop_page = 10

link_path_to_lots = "/etp/trade/inner-view-lots.html?perspective=inline&id="

data_origin = {
    "etp_profit": "https://www.etp-profit.ru/",
    "ausib": "https://ausib.ru/",
    "seltim": "https://www.seltim.ru/",
    "atctrade": "https://atctrade.ru/",
    "regtorg": "https://regtorg.com/",
    "aukcioncenter": "https://aukcioncenter.ru/",
    "torgidv": "https://torgidv.ru/",
    "ptp_center": "https://ptp-center.ru/",
}

serp_link = {
    "etp_profit": "https://www.etp-profit.ru/etp/trade/list.html",
    "ausib": "https://ausib.ru/etp/trade/list.html",
    "seltim": "https://www.seltim.ru/etp/trade/list.html",
    "atctrade": "https://atctrade.ru/etp/trade/list.html",
    "regtorg": "https://regtorg.com/etp/trade/list.html",
    "aukcioncenter": "https://aukcioncenter.ru/etp/trade/list.html",
    "torgidv": "https://torgidv.ru/etp/trade/list.html",
    "ptp_center": "https://ptp-center.ru/etp/trade/list.html",
}

lot_link = {
    "etp_profit": "https://www.etp-profit.ru/etp/trade/inner-view-lots.html?perspective=inline&id=",
    "ausib": "https://ausib.ru/etp/trade/inner-view-lots.html?perspective=inline&id=",
    "seltim": "https://www.seltim.ru/etp/trade/inner-view-lots.html?perspective=inline&id=",
    "atctrade": "https://atctrade.ru/etp/trade/inner-view-lots.html?perspective=inline&id=",
    "regtorg": "https://www.regtorg.com/etp/trade/inner-view-lots.html?perspective=inline&id=",
    "aukcioncenter": "https://aukcioncenter.ru/etp/trade/inner-view-lots.html?perspective=inline&id=",
    "torgidv": "https://torgidv.ru/etp/trade/inner-view-lots.html?perspective=inline&id=",
    "ptp_center": "https://ptp-center.ru/etp/trade/inner-view-lots.html?perspective=inline&id=",
}

doc_link = {
    "etp_profit": "https://www.etp-profit.ru/edoc/attachments/list.html?perspective=inline&id=",
    "ausib": "https://ausib.ru/edoc/attachments/list.html?perspective=inline&id=",
    "seltim": "https://www.seltim.ru/edoc/attachments/list.html?perspective=inline&id=",
    "atctrade": "https://atctrade.ru/edoc/attachments/list.html?perspective=inline&id=",
    "regtorg": "https://www.regtorg.com/edoc/attachments/list.html?perspective=inline&id=",
    "aukcioncenter": "https://aukcioncenter.ru/edoc/attachments/list.html?perspective=inline&id=",
    "torgidv": "https://torgidv.ru/edoc/attachments/list.html?perspective=inline&id=",
    "ptp_center": "https://ptp-center.ru/edoc/attachments/list.html?perspective=inline&id=",
}

url_file = {
    "etp_profit": "https://www.etp-profit.ru",
    "ausib": "https://ausib.ru",
    "seltim": "https://www.seltim.ru",
    "atctrade": "https://atctrade.ru",
    "regtorg": "https://www.regtorg.com",
    "aukcioncenter": "https://aukcioncenter.ru",
    "torgidv": "https://torgidv.ru",
    "ptp_center": "https://ptp-center.ru",
}

query_param = {
    "subject": "",
    "number": "",
    "numberOfLot": "",
    "debtorTitle": "",
    "organizerTitle": "",
    "arbitrationManagerTitle": "",
    "bidSubmissionStartDateFrom": start_date,
    "bidSubmissionStartDateTo": "",
    "bidSubmissionEndDateFrom": "",
    "bidSubmissionEndDateTo": "",
    "procurementMethod": "any",
    "procurementClassifier": "",
    "processStatus": "any",
    "eventSubmit_doLis": "%CF%EE%E8%F1%EA",
    "eventSubmit_doList": "",
}
