import re
from idlelib.run import Executive

import xmltodict
from bs4 import BeautifulSoup

from app.crawlers.crawler_sberbank.crawler_sberbank.utils.config import main_urls
from app.crawlers.crawler_sberbank.crawler_sberbank.utils.manage_spider import (
    deep_get_dict,
    sort_trading_type,
)
from app.db.models import DownloadData
from app.utils import Contacts, dedent_func, DateTimeHelper


class NewCombo:
    def __init__(self, response):
        self.response = response
        self.soup = BeautifulSoup(response.text, "lxml")
        self.data = xmltodict.parse(self.soup.find("input", id="xmlData").get("value"))

    @property
    def trading_id(self):
        return deep_get_dict(
            self.data, "Purchase.PurchaseInfoTotal.PurchaseInfo.PurchaseId"
        )

    @property
    def trading_link(self):
        return self.response.url

    @property
    def trading_number(self):
        return deep_get_dict(
            self.data, "Purchase.PurchaseInfoTotal.PurchaseInfo.PurchaseCode"
        )

    @property
    def trading_type(self):
        trading_type = sort_trading_type(
            deep_get_dict(
                self.data,
                "Purchase.PurchaseInfoTotal.PurchaseInfo.PurchaseTypeInfo.PurchaseTypeName",
            )
        )
        return trading_type

    @property
    def trading_form(self):
        return "open"

    @property
    def trading_org(self):
        org = deep_get_dict(
            self.data, "Purchase.PurchaseInfoTotal.OrganizatorInfo.orgname"
        )
        return "".join(re.sub(r"\s+", " ", org))

    @property
    def trading_org_inn(self):
        inn = deep_get_dict(
            self.data, "Purchase.PurchaseInfoTotal.OrganizatorInfo.orginn"
        )
        return Contacts.check_inn(inn)

    @property
    def trading_org_contacts(self):
        phone = deep_get_dict(
            self.data,
            "Purchase.PurchaseInfoTotal.ContactInfo.ContactPhone",
        )
        email = deep_get_dict(
            self.data,
            "Purchase.PurchaseInfoTotal.ContactInfo.ContactEmail",
        )
        return {
            "phone": Contacts.check_phone(phone),
            "email": Contacts.check_email(email),
        }

    @property
    def address(self):
        return deep_get_dict(
            self.data, "Purchase.PurchaseInfoTotal.OrganizatorInfo.orgaddressjur"
        )

    @property
    def lot_id(self):
        return deep_get_dict(self.data, "Purchase.Bids.Bid.BidInfoTotal.BidInfo.BidId")

    @property
    def lot_number(self):
        number = deep_get_dict(
            self.data, "Purchase.Bids.Bid.BidInfoTotal.BidInfo.BidNo"
        )
        if number != "1":  # FIXME: delete
            pass
        return number

    @property
    def short_name(self):
        return dedent_func(
            deep_get_dict(self.data, "Purchase.Bids.Bid.BidInfoTotal.BidInfo.BidName")
        )

    @property
    def start_price(self): ...

    @property
    def step_price(self): ...

    @property
    def start_date_requests(self):
        date = deep_get_dict(
            self.data,
            "Purchase.PurchasePlan.ApplSubmissionInfo.ApplSubmissionStartDate",
        ) or deep_get_dict(
            self.data,
            "Purchase.PurchaseInfoTotal.ApplSubmissionInfo.ApplSubmissionStartDate",
        )
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def end_date_requests(self):
        date = deep_get_dict(
            self.data,
            "Purchase.PurchasePlan.ApplSubmissionInfo.ApplSubmissionStopDate",
        ) or deep_get_dict(
            self.data,
            "Purchase.PurchaseInfoTotal.ApplSubmissionInfo.ApplSubmissionStopDate",
        )
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def start_date_trading(self):
        return None  # TODO

    @property
    def end_date_trading(self):
        date = deep_get_dict(
            self.data,
            "Purchase.PurchaseInfoTotal.SummingupInfo.SummingupDate",
        )
        try:
            return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            return None

    def download(self, cookies: str, property_type: str, org: str = None):
        files = []
        for file in deep_get_dict(
            self.data,
            "Purchase.PurchaseDocumentationInfo.PurchaseDocumentationDocsInfo.Docs.file",
        ) or deep_get_dict(
            self.data,
            "Purchase.PurchaseDocumentationInfo.PurchaseDocumentationDocsInfo.DocFiles.document",
        ):
            name = file.get("filename") or file.get("fileName")
            if not (link := file.get("url")):
                main_url = main_urls[property_type]
                if org:
                    main_url = main_url[org]
                link = f"{main_url}/File/DownloadFile?fid={file['fileid']}"
            files.append(DownloadData(file_name=name, url=link, cookies=cookies))
        return files
