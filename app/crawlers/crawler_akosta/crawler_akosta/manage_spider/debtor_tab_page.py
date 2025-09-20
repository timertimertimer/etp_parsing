import re
from app.utils import dedent_func, logger, Contacts


class DebtorTab:
    def __init__(self, _response, soup):
        self.response = _response
        self.soup = soup

    def find_correct_form_number_collapsed(self):
        return [
            tag.get("id")
            for tag in self.soup.find_all(
                "input", id=re.compile("formMain:j_idt\d+_collapsed")
            )
        ]

    def find_correct_form_number(self):
        link = self.soup.find("a", onclick=re.compile(r"mojarra\.jsfcljs"))
        pattern = r"\{'(formMain:j_idt\d+)':'\1'\}"
        match = re.search(pattern, link["onclick"])
        if match:
            form_number = match.group(1)
            return form_number
        logger.warning(
            f"{self.response.url} | Не удалось найти динамический идентификатор"
        )
        return None

    @property
    def trading_number(self):
        try:
            trading_number = self.soup.find(
                "label", string=re.compile("Номер торгов в ЕФРСБ", re.IGNORECASE)
            )
            if trading_number:
                tn = trading_number.parent
                tn = tn.get_text().strip().split(":")[-1].strip()
                return tn
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR trading number {ex}")
        return None

    @property
    def msg_number(self):
        try:
            msg_number = self.soup.find(
                "label",
                string=re.compile("Номер объявления о торгах в ЕФРСБ", re.IGNORECASE),
            )
            if msg_number:
                msg = msg_number.parent
                msg = msg.get_text().strip().split(":")[-1].strip()
                if re.match(r"\d{6,8}", msg):
                    msg = re.findall(r"\d{7,8}", msg)
                    return " ".join(msg)
                else:
                    logger.warning(
                        f"{self.response.url} | ERROR message number CHECK REAL VALUE!"
                    )
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR message number {ex}")
        return None

    @property
    def case_number(self):
        try:
            case_number = self.soup.find(
                "label", string=re.compile("дела о банкротстве", re.IGNORECASE)
            )
            if case_number:
                case = case_number.parent
                case = case.get_text().strip().split(":")[-1].strip()
                return Contacts.check_case_number(case)
        except Exception as ex:
            logger.warning(f"{self.response.url} | ERROR case number {ex}")
        return None

    @property
    def debtor_inn(self):
        try:
            div_debtor = self.soup.find("div", string="Должник")
            if div_debtor:
                div_debtor = div_debtor.parent
                inn_deb = div_debtor.find(
                    "label", string=re.compile("ИНН", re.IGNORECASE)
                )
                if inn_deb:
                    inn_deb = dedent_func(
                        inn_deb.parent.get_text().strip().split(":")[-1].strip()
                    )
                    if re.match(r"\d{10,12}", inn_deb):
                        return inn_deb
            else:
                logger.warning(f"{self.response.url} | INVALID DATA DEBTOR INN (1)")
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA DEBTOR INN {ex}")
        return None

    @property
    def debtor_address(self):
        try:
            address = None
            div_debtor = self.soup.find("div", string="Должник")
            div_sud = self.soup.find("div", string="Реквизиты судебного акта")
            if div_debtor:
                div_debtor = div_debtor.parent
                address = div_debtor.find(
                    "label", string=re.compile("Юридический адрес", re.IGNORECASE)
                ) or div_debtor.find(
                    "label", string=re.compile("Почтовый адрес", re.IGNORECASE)
                )
                if address:
                    address = address.parent.get_text(strip=True).split(":")[-1]
            if not address:
                if div_sud:
                    div_sud = div_debtor.parent
                    address = div_sud.find(
                        "label", string=re.compile("Наименование суда", re.IGNORECASE)
                    )
                    if address:
                        address = address.parent.get_text(strip=True).split(":")[-1]
            return dedent_func(address)
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA DEBTOR ADDRESS {ex}")
        return None

    def return_arbitrator_form(self):
        arb = self.soup.find("div", string="Арбитражный/конкурсный управляющий")
        if arb:
            return arb.parent
        return None

    @property
    def arbit_manager(self):
        try:
            arb = self.return_arbitrator_form()

            last_name = arb.find("label", string=re.compile("Фамилия", re.IGNORECASE))
            if last_name:
                last = last_name.parent
                last = dedent_func(last.get_text().strip().split(":")[-1].strip())
            else:
                logger.warning(f"{self.response.url} | CHECK IF LAST NAME")
                last = ""

            first_name = arb.find("label", string=re.compile("Имя", re.IGNORECASE))
            if first_name:
                first = first_name.parent
                first = dedent_func(first.get_text().strip().split(":")[-1].strip())
            else:
                logger.warning(f"{self.response.url} | CHECK IF FIRST NAME")
                first = ""

            middle_name = arb.find(
                "label", string=re.compile("Отчество", re.IGNORECASE)
            )
            if middle_name:
                middle = middle_name.parent
                middle = dedent_func(middle.get_text().strip().split(":")[-1].strip())
            else:
                middle = ""
            return " ".join([last, first, middle])
        except Exception as e:
            logger.warning(f"{self.response.url} | ERROR ARBITR NAME {e}")
        return None

    @property
    def arbit_manager_inn(self):
        try:
            arb = self.return_arbitrator_form()
            _inn = arb.find("label", string=re.compile("ИНН", re.IGNORECASE))
            if _inn:
                _inn = _inn.parent
                _inn = dedent_func(_inn.get_text().strip().split(":")[-1].strip())
                if re.match(r"\d{10,12}", _inn):
                    return _inn
                else:
                    logger.warning(f"{self.response.url} | CHECK INN ARBITRATOR")
        except Exception as ex:
            logger.warning(f"{self.response.url} | INVALID DATA ARBITR {ex}")
        return None

    @property
    def arbit_manager_org(self):
        arb = self.return_arbitrator_form()
        try:
            sro = arb.find("label", string=re.compile("СРО", re.IGNORECASE))
        except Exception as e:
            return None
        if sro:
            sro = sro.parent
            sro = dedent_func(sro.get_text().strip().split(":")[-1].strip())
            return sro
        else:
            return None
