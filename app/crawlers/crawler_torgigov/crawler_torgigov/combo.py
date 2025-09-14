from datetime import datetime
from typing import Optional

from app.utils import dedent_func, Contacts, DateTimeHelper, logger
from app.db.models import DownloadData


class Combo:
    def __init__(self, data):
        self.data = data

    def get_lots(self):
        return self.data["lots"]

    def download_general(self):
        files = list()
        attachments = self.data.get("attachments", [])
        for file in attachments:
            link = f"https://torgi.gov.ru/new/file-store/v1/{file['fileId']}"
            name = file["fileName"]
            files.append(DownloadData(url=link, file_name=name))
        return files

    def download_lot(self, lot):
        files = list()
        attachments = lot.get("attachments", [])
        image_ids = lot.get("imageIds", [])
        i = 0
        for file in attachments:
            link = f"https://torgi.gov.ru/new/file-store/v1/{file['fileId']}"
            name = file["fileName"]
            if file["fileId"] in image_ids:
                files.append(DownloadData(url=link, file_name=name, is_image=True, order=i))
                i += 1
            else:
                files.append(DownloadData(url=link, file_name=name))
        return files

    @property
    def trading_id(self):
        return self.data["id"]

    @property
    def trading_link(self):
        return f"https://torgi.gov.ru/new/public/notices/view/{self.trading_id}"

    @property
    def trading_number(self):
        return self.trading_id

    @property
    def trading_type(self):
        type_value = self.data["biddForm"]["name"]
        if type_value == "Сообщение о предоставлении (реализации)":
            return None
        d = {
            "auction": ["Электронный аукцион", "Аукцион"],
            "offer": [
                "Публичное предложение",
                "Публичное предложение (цессия)",
                "Публичное предложение (ЗК РФ)",
                "Предложение о заключении концессионного соглашения"
            ],
            "competition": ["Электронный конкурс", "Конкурс"],
        }
        for key in d:
            if type_value in d[key]:
                return key
        logger.error(f"{self.trading_link} | Unknown trading type {type_value}")
        return None

    @property
    def trading_form(self):
        return "open"

    @property
    def trading_org(self):
        return dedent_func(self.data["bidderOrg"]["name"])

    @property
    def trading_org_inn(self):
        return Contacts.check_inn(self.data["bidderOrg"]["inn"])

    @property
    def trading_org_contacts(self):
        return {
            "email": Contacts.check_email(self.data["bidderOrg"]["email"]),
            "phone": Contacts.check_phone(self.data["bidderOrg"]["tel"]),
        }

    @property
    def debtor_inn(self):
        return

    def get_address(self, lot):
        return lot.get("estateAddress") or lot.get("rightHolderOrg", {}).get(
            "legalAddress"
        )

    @property
    def arbit_manager(self):
        return self.data["bidderOrg"]["contPerson"]

    @property
    def status(self):
        form_value = self.data["noticeStatus"]
        d = {
            "active": ["APPLICATIONS_SUBMISSION", "PUBLISHED"],
            "pending": ["DETERMINING_WINNER"],
            "ended": ["CANCELED", "COMPLETED"],
        }
        for key in d:
            if form_value in d[key]:
                return key
        logger.error(f"{self.trading_link} | Unknown trading form {form_value}")
        return None

    def get_category(self, lot):
        return lot["category"]["name"]

    def get_lot_id(self, lot):
        return lot["id"]

    def get_lot_link(self, lot):
        return f"https://torgi.gov.ru/new/public/lots/lot/{self.get_lot_id(lot)}/(lotInfo:info)?fromRec=false#lotInfoSection-info"

    def get_lot_number(self, lot):
        return lot["lotNumber"]

    def get_short_name(self, lot):
        return lot["lotName"]

    def get_lot_info(self, lot):
        return lot["lotDescription"]

    def get_deposit(self, lot):
        return lot["deposit"]

    @property
    def property_information(self):
        return

    @property
    def start_date_requests(self) -> Optional[datetime]:
        # "biddStartTime":"2025-08-05T06:00:00Z" + timezoneOffsetAbbreviation
        return DateTimeHelper.smart_parse(self.data["biddStartTime"])

    @property
    def end_date_requests(self) -> Optional[datetime]:
        return DateTimeHelper.smart_parse(self.data["biddEndTime"])

    @property
    def start_date_trading(self) -> Optional[datetime]:
        if date := self.data.get("auctionStartDate"):
            return DateTimeHelper.smart_parse(date)
        return None

    @property
    def end_date_trading(self) -> Optional[datetime]:
        date = None
        if self.trading_type == "offer":
            date = self.data["auctionStartDate"]
        elif self.trading_type in ["auction", "competition"]:
            for el in self.data["attributes"]:
                if el["fullName"] in [
                    "Дата, время подведения результатов торгов",
                    "Дата и время подведения итогов аукциона",
                    "Дата и время проведения конкурса"
                ]:
                    date = el.get("value")
        else:
            pass
        if date:
            return DateTimeHelper.smart_parse(date)
        return None

    def get_start_price(self, lot):
        return lot.get("priceMin")

    def get_step_price(self, lot):
        return lot.get("priceStep")

    @property
    def periods(self):
        return
