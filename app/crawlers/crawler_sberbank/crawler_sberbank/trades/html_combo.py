import re

import xmltodict
from bs4 import BeautifulSoup

from app.crawlers.crawler_sberbank.crawler_sberbank.utils.config import main_urls
from app.crawlers.crawler_sberbank.crawler_sberbank.utils.manage_spider import (
    deep_get_dict,
    sort_trading_type,
)
from app.db.models import DownloadData
from app.utils import Contacts, dedent_func, DateTimeHelper, make_float
from app.utils.config import default_user_agent


class NewCombo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")
        try:
            self.data = xmltodict.parse(
                self.soup.find("input", id="xmlData").get("value")
            )
            self.data = self.data.get("Purchase") or self.data.get("PurchaseView")
        except Exception as e:
            raise e

    @property
    def purchase_info(self):
        return (
            deep_get_dict(self.data, "PurchaseInfoTotal.PurchaseInfo")
            or deep_get_dict(self.data, "PurchaseMainInfo")
            or deep_get_dict(self.data, "PurchaseInfo.PurchaseMainInfo")
        )

    @property
    def trading_id(self):
        return self.purchase_info.get("PurchaseID") or self.purchase_info.get(
            "PurchaseId"
        )

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return self.purchase_info["PurchaseCode"]

    @property
    def trading_type(self):
        trading_type = (
            deep_get_dict(self.purchase_info, "PurchaseTypeInfo.PurchaseTypeName")
            or deep_get_dict(
                self.data,
                "PurchaseInfoTotal.PurchaseOrderInfo.PurchasePurchaseTypeCustomName",
            )
            or self.purchase_info.get("PurchaseTypeName")
        )
        if not trading_type:
            return None
        trading_type = sort_trading_type(trading_type)
        return trading_type

    @property
    def trading_form(self):
        return "open"

    @property
    def trading_org(self):
        org = (
            deep_get_dict(self.data, "PurchaseInfoTotal.OrganizatorInfo.orgname")
            or deep_get_dict(self.data, "OrganizatorInfo.orgname")
            or deep_get_dict(self.data, "PurchaseInfo.OrganizatorInfo.orgname")
        )
        return "".join(re.sub(r"\s+", " ", org))

    @property
    def trading_org_inn(self):
        inn = (
            deep_get_dict(self.data, "PurchaseInfoTotal.OrganizatorInfo.orginn")
            or deep_get_dict(self.data, "OrganizatorInfo.orginn")
            or deep_get_dict(self.data, "PurchaseInfo.OrganizatorInfo.orginn")
        )
        return Contacts.check_inn(inn)

    @property
    def trading_org_contacts(self):
        phone = (
            deep_get_dict(
                self.data,
                "PurchaseInfoTotal.ContactInfo.ContactPhone",
            )
            or deep_get_dict(self.data, "OrganizatorInfo.orgphone")
            or deep_get_dict(self.data, "PurchaseInfo.OrganizatorInfo.orgphone")
        )
        email = (
            deep_get_dict(
                self.data,
                "PurchaseInfoTotal.ContactInfo.ContactEmail",
            )
            or deep_get_dict(self.data, "OrganizatorInfo.orgemail")
            or deep_get_dict(self.data, "PurchaseInfo.OrganizatorInfo.orgemail")
        )
        return {
            "phone": Contacts.check_phone(phone),
            "email": Contacts.check_email(email),
        }

    @property
    def address(self):
        return (
            deep_get_dict(self.data, "PurchaseInfoTotal.OrganizatorInfo.orgaddressjur")
            or deep_get_dict(self.data, "OrganizatorInfo.orgaddressjur")
            or deep_get_dict(self.data, "PurchaseInfo.OrganizatorInfo.orgaddressjur")
        )

    def get_lots(self):
        lots = deep_get_dict(self.data, "Bids.Bid")
        if isinstance(lots, dict):
            lots = [lots]
        return lots

    def lot_id(self, lot: dict):
        return deep_get_dict(lot, "BidInfoTotal.BidInfo.BidId") or deep_get_dict(
            lot, "BidInfo.BidId"
        )

    def lot_number(self, lot: dict):
        number = deep_get_dict(lot, "BidInfoTotal.BidInfo.BidNo") or deep_get_dict(
            lot, "BidInfo.BidNo"
        )
        return number

    def short_name(self, lot: dict):
        return dedent_func(
            deep_get_dict(lot, "BidInfoTotal.BidInfo.BidName")
            or deep_get_dict(lot, "BidInfo.BidName")
        )

    def start_price(self, lot: dict):
        return make_float(
            deep_get_dict(
                lot,
                "BidInfoTotal.BidPriceInfo.BidPrice",
            )
            or deep_get_dict(lot, "BidInfo.BidPrice"),
        )

    @property
    def step_price(self):
        return None  # TODO

    @property
    def start_date_requests(self):
        date = (
            deep_get_dict(
                self.data,
                "PurchasePlan.ApplSubmissionInfo.ApplSubmissionStartDate",
            )
            or deep_get_dict(
                self.data,
                "PurchaseInfoTotal.ApplSubmissionInfo.ApplSubmissionStartDate",
            )
            or deep_get_dict(self.data, "PurchasePlan.RequestStartDate")
            or deep_get_dict(self.data, "PurchaseInfo.PurchasePlan.PurchaseRequestStartDate")
        )
        try:
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            return None

    @property
    def end_date_requests(self):
        date = (
            deep_get_dict(
                self.data,
                "PurchasePlan.ApplSubmissionInfo.ApplSubmissionStopDate",
            )
            or deep_get_dict(
                self.data,
                "PurchaseInfoTotal.ApplSubmissionInfo.ApplSubmissionStopDate",
            )
            or deep_get_dict(self.data, "PurchasePlan.RequestStopDate")
            or deep_get_dict(self.data, "PurchaseInfo.PurchasePlan.PurchaseRequestStopDate")
        )
        try:
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            return None

    @property
    def start_date_trading(self):
        date = deep_get_dict(
            self.data,
            "PurchasePlan.ProcedureStartDate",
        )
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_trading(self):
        date = deep_get_dict(
            self.data,
            "PurchaseInfoTotal.SummingupInfo.SummingupDate",
        )
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    def download(self, cookies: str, property_type: str, org: str = None):
        files = []
        documents = (
            deep_get_dict(
                self.data,
                "PurchaseDocumentationInfo.PurchaseDocumentationDocsInfo.Docs.file",
            )
            or deep_get_dict(
                self.data,
                "PurchaseDocumentationInfo.PurchaseDocumentationDocsInfo.DocFiles.document",
            )
            or deep_get_dict(self.data, "DocsDiv.Docs.file")
            or deep_get_dict(self.data, "Docs.AuctionDocs.file")
        )
        if isinstance(documents, dict):
            documents = [documents]
        for file in documents:
            name = file.get("filename") or file.get("fileName")
            if not (link := file.get("url")):
                main_url = main_urls[property_type]
                if org:
                    main_url = main_url[org]
                link = f"{main_url}/File/DownloadFile?fid={file['fileid']}"
            dd = DownloadData(file_name=name, url=link)
            if "sberbank" in link:
                dd.headers = {"User-Agent": default_user_agent, "Referer": self.response.url, "Cookie": cookies}
            files.append(dd)
        return files
