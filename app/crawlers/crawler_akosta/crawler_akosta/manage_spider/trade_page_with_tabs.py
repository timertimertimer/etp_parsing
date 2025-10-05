import re

from app.utils import dedent_func, DateTimeHelper, Contacts, logger


class TradePage:
    def __init__(self, _response, soup):
        self.response = _response
        self.soup = soup

    @property
    def get_lot_div_sector(self):
        try:
            div_lot = self.soup.find("div", id="formMain:dataLot").find(
                "tbody", id="formMain:dataLot_data"
            )
            return div_lot
        except Exception as ex:
            logger.warning(f"{self.response.url} | {ex}")
        return None

    def get_post_lot_data(self):
        try:
            lst_a = list()
            for a in self.get_lot_div_sector.find_all("a"):
                lst_a.append(a.get("id"))
            return lst_a
        except Exception as ex:
            logger.warning(f"{self.response.url} | {ex}")
        return None

    @property
    def trading_type(self):
        try:
            trading_type = self.soup.find(
                "label", string=re.compile("Вид торгов", re.IGNORECASE)
            ).parent
            trading_type = dedent_func(
                trading_type.get_text().strip().split(".")[-1].strip()
            )
            offer = ("Продажа посредством публичного предложения",)
            auction = (
                "Открытый аукцион с открытой формой подачи предложений",
                "Открытый аукцион с закрытой формой подачи предложений",
            )
            competition = (
                "Открытый конкурс с открытой формой подачи предложений",
                "Открытый конкурс с закрытой формой подачи предложений",
            )

            if trading_type in offer:
                return "offer"
            elif trading_type in auction:
                return "auction"
            elif trading_type in competition:
                return "competition"
        except Exception as ex:
            logger.warning(f"{self.response.url} | {ex}")
        return None

    @property
    def trading_form(self):
        trading_form = self.soup.find(
            "label", string=re.compile("Вид торгов", re.IGNORECASE)
        ).parent
        trading_form = dedent_func(
            trading_form.get_text().strip().split(".")[-1].strip()
        )
        _open = (
            "Продажа посредством публичного предложения",
            "Открытый аукцион с открытой формой подачи предложений",
            "Открытый аукцион с закрытой формой подачи предложений",
            "Открытый конкурс с открытой формой подачи предложений",
            "Открытый конкурс с закрытой формой подачи предложений",
        )
        if trading_form in _open:
            return "open"
        logger.warning(f"{self.response.url} | ERROR TRADING FORM")
        return None

    def return_org_text(self):
        try:
            div_organizer = self.soup.find(
                "a", title="Перейти на карту организатора"
            ).parent
            return div_organizer
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR ORG TEXT - {ex}")
        return None

    @property
    def trading_org(self):
        try:
            _div = self.return_org_text()
            return dedent_func(" ".join(_div.a.get_text().strip().split()))
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR org name {ex}")
        return None

    @property
    def email(self):
        try:
            _div = self.return_org_text()
            pattern_mail = re.compile(
                r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)"
            )
            email = pattern_mail.findall(_div.get_text().strip())
            return Contacts.check_email(email[0])
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR organizer email {ex}")
        return None

    @property
    def phone(self):
        _div = self.return_org_text()
        p_in_div = _div.find_all("p")
        if len(p_in_div) > 0:
            phone = "".join(
                [
                    p.get_text().strip()
                    for p in p_in_div
                    if "Тел." in p.get_text().strip()
                ]
            )
            phone = "".join(
                [
                    x
                    for x in phone.split(":")[-1]
                    if x.isdigit() or x == "+" or x == "(" or x == ")" or x == " "
                ]
            )
            phone = phone.strip()
            if len(phone) > 5:
                return Contacts.check_phone(phone)
        return None

    @property
    def trading_org_contacts(self) -> dict | None:
        try:
            return {"email": self.email, "phone": self.phone}
        except Exception as e:
            logger.warning(f"{self.response.url} | func get_org_contacts {e}")
        return None

    def get_lot_number(self, _id):
        try:
            tr = self.soup.find("a", id=_id)
            if tr:
                tr = tr.parent.parent
                if tr:
                    tr = tr.find("td").get_text()
                    return tr
        except Exception as ex:
            logger.warning(f"{self.response.url} | {ex}")
        return None

    def start_date_trading_auc(self):
        try:
            start = self.soup.find(
                "label",
                string=re.compile("Дата и время начала аукциона", re.IGNORECASE),
            )
            if start:
                start = start.parent
                start = dedent_func(
                    start.get_text().strip().split(":", maxsplit=1)[-1].strip()
                )
                start = re.sub(r"\s+", " ", start)
                start = "".join(
                    re.findall(r"\d{1,2}.\d{1,2}.\d{2,4}\s\s?\d{1,2}:\d{1,2}", start)[0]
                )
                if start:
                    return DateTimeHelper.smart_parse(start).astimezone(DateTimeHelper.moscow_tz)
                else:
                    logger.warning(
                        f"{self.response.url} | START DATE WAS NOT FOUND (2)"
                    )
            else:
                logger.warning(f"{self.response.url} | START DATE WAS NOT FOUND (1)")
        except Exception as e:
            logger.warning(
                f"{self.response.url} | ERROR start date request auction {e}"
            )
        return None

    def end_date_end_auc(self):
        try:
            end = self.soup.find(
                "label",
                string=re.compile("Дата и время завершения аукциона", re.IGNORECASE),
            )
            if end:
                end = end.parent
                end = dedent_func(
                    end.get_text().strip().split(":", maxsplit=1)[-1].strip()
                )
                end = re.sub(r"\s+", " ", end)
                end = "".join(
                    re.findall(r"\d{1,2}.\d{1,2}.\d{2,4}\s\s?\d{1,2}:\d{1,2}", end)[0]
                )
                if end:
                    return DateTimeHelper.smart_parse(end).astimezone(DateTimeHelper.moscow_tz)
                else:
                    logger.warning(f"{self.response.url} | END DATE WAS NOT FOUND (2)")
            else:
                logger.warning(f"{self.response.url} | END DATE WAS NOT FOUND (1)")
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR end date request auction {e}")
        return None

    def return_period_trading_auc(self) -> list or None:
        try:
            period_auc = self.soup.find(
                "label", string=re.compile("Период приема заявок", re.IGNORECASE)
            )
            period_auc = dedent_func(
                period_auc.parent.get_text().strip().split(":", maxsplit=1)[-1].strip()
            )
            period_auc = re.sub(r"\s+", " ", period_auc)
            pattern_perio_auc = re.compile(
                r"\d{1,2}.\d{1,2}.\d{2,4}\s\s?\d{1,2}:\d{1,2}"
            )
            lst_start_trading = pattern_perio_auc.findall(period_auc)
            return lst_start_trading
        except Exception as e:
            logger.warning(
                f"{self.response.url} | ERROR during return periods of trading auction {e}"
            )
        return None

    def start_date_request_auc(self):
        try:
            lst = self.return_period_trading_auc()
            if 1 <= len(lst) < 3:
                _date = DateTimeHelper.smart_parse(lst[0]).astimezone(DateTimeHelper.moscow_tz)
                return _date
            else:
                logger.warning(
                    f"{self.response.url} | check data for start date trading auction "
                )
        except Exception as e:
            logger.warning(
                f"{self.response.url} | ERROR START DATE TRADING AUCTION {e}"
            )
        return None

    def end_date_request_auc(self):
        try:
            lst = self.return_period_trading_auc()
            if len(lst) == 2:
                _date = DateTimeHelper.smart_parse(lst[1]).astimezone(DateTimeHelper.moscow_tz)
                return _date
            else:
                logger.warning(
                    f"{self.response.url} | check data for END date trading auction "
                )
        except Exception as e:
            logger.warning(
                f"{self.response.url} | ERROR START DATE TRADING AUCTION {e}"
            )
        return None
