Обеспечение заявки (Кап ремонт, 223фз, закупки юр лиц)
- Размер обеспечения заявки на участие в электронном аукционе (Кап ремонт) https://zakupki.gov.ru/epz/order/notice/ea615/view/common-info.html?regNumber=078800000012500023
- Размер обеспечения заявки (Кап ремонт) https://utp.sberbank-ast.ru/GKH/NBT/PurchaseView/4/0/0/3070381
- Обеспечение заявки (Кап ремонт) https://www.roseltorg.ru/procedure/057270000012500987
- ??? Обеспечительный платеж (223фз, закупки юр лиц) https://www.fabrikant.ru/v2/trades/procedure/view/KiasuCnK0IGchhE_5WlDAQ https://www.fabrikant.ru/v2/trades/procedure/view/hwFT_QB6Bsxt37kTsxsdzg
- ??? Обеспечение оплаты услуг оператора (223фз) https://utp.sberbank-ast.ru/Trade/NBT/PurchaseView/22/0/0/3071093
- Размер обеспечения заявки (закупки юр лиц) https://torgi.etpu.ru/app/LotCard/page?LotCard.lotEntity=LT%3Acorebofs002080000nlr6nu3b1jjen38

Обеспечение обязательств по договору (Кап ремонт, 223фз, закупки юр лиц)
- Размер обеспечения исполнения обязательств по договору (Кап ремонт) https://zakupki.gov.ru/epz/order/notice/ea615/view/common-info.html?regNumber=078800000012500023
- Размер обеспечения исполнения обязательств по договору (Кап ремонт) https://utp.sberbank-ast.ru/GKH/NBT/PurchaseView/4/0/0/3070381
- Обеспечение контракта (Кап ремонт) https://www.roseltorg.ru/procedure/057270000012500987
- Размер обеспечения исполнения договора (223фз) https://utp.sberbank-ast.ru/Trade/NBT/PurchaseView/22/0/0/3071093
- Размер обеспечения исполнения договора (закупки юр лиц) https://torgi.etpu.ru/app/LotCard/page?LotCard.lotEntity=LT%3Acorebofs002080000nlr6nu3b1jjen38

sme = Small and Medium-sized Enterprises

контрагенты сохраняются в базе без валидации по другим ресурсам (федресурс, проверка инн, фио и тп)

при написании обработчика страницы с информацией по торгам/лотам (combo.py) необходимо учитывать следующие моменты:
!!!ОЧЕНЬ ВАЖНО!!!
- даты необходимо сохранять с таймзоной сайта

```python
d = {
    "offer": ["Публичное предложение продавца", "Процедура с поэтапным снижением цены"],
    "auction": [
        "Открытый аукцион с открытой формой подачи ценовых предложений",
        "Открытый аукцион с закрытой формой подачи ценовых предложений",
        "Закрытый аукцион с открытой формой подачи ценовых предложений",
        "Закрытый аукцион с закрытой формой подачи ценовых предложений",
        "Аукцион продавца",
        "Аукцион",
        "Аукцион с закрытой формой подачи предложений о цене",
        "Аукцион с открытой формой подачи предложений о цене",
        "Публичное предложение (по типу голландского аукциона)",
        "Аукцион в электронной форме, участниками которого могут быть только субъекты малого и среднего предпринимательства"
    ],
    "competition": [
        "Открытый конкурс", "Закрытый конкурс", "Конкурс продавца",
        "Конкурс в электронной форме, участниками которого могут являться только субъекты малого и среднего предпринимательства",
        "Конкурс"
    ],
    "pdo": ["ПДО продавца (по типу продажи без объявления цены)", "МПДО"],
    "rfp": [
        "Запрос предложений",
        "Запрос предложений в электронной форме, участниками которого могут являться только субъекты малого и среднего предпринимательства",
        "Запрос цен", "Запрос котировок", "Запрос оферт", "Мониторинг цен",
        "Запрос котировок в электронной форме, участниками которого могут являться только субъекты малого и среднего предпринимательства"
    ],
    "tender": ["Тендер"],
    "reduction": ["Редукцион"]
}
```

для сбера (sberbank) и росельторга (roseltorg) нужны прокси 
proxies template `user:pass@ip:port`

отказались от sales.lot-online.ru, catalog.lot-online.ru пришел на замену с теми же лотами

карусели
- akosta https://www.akosta.info/akosta/lotCard.xhtml?parm=707267682048474C573E6F727758716C6720375F3834353B
- ei https://ei.ru/lot/3102080
- heveya https://heveya.ru/lot/4206964
- kartoteka https://www.kartoteka.ru/property/?id=4003135
- lot_online_catalog https://catalog.lot-online.ru/index.php?dispatch=products.view&product_id=1141955
- lot_online_old https://rad.lot-online.ru/lot/details.html?lotId=174164003
- lot_online_zalog https://zalog.lot-online.ru/user/collateral/catalog_page.html?id=766696005
- mets https://m-ets.ru/177064-1
- torgigov https://torgi.gov.ru/new/public/lots/lot/21000031920000000258_5/(lotInfo:info)?fromRec=false

скачивание файлов
- akosta general POST, lot GET