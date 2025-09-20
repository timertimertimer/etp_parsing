import re

from app.utils import dedent_func, Contacts, logger, DateTimeHelper, make_float
from ..utils.manage_spider import deep_get_dict, sort_trading_type, get_trading_form
from bs4 import BeautifulSoup as BS


class AuctionParse:
    addresses = dict()

    def __init__(self, data, url):
        self.url = url
        self.data = data

    @property
    def trading_id(self):
        try:
            pattern = re.compile("\d+$")
            return "".join(pattern.findall(self.url))
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA TRADING ID")
        return None

    @property
    def trading_link(self):
        return self.url

    @property
    def purchase_info(self):
        return (
            deep_get_dict(self.data, "Purchase.PurchaseinfoPanel.PurchaseInfo")
            or deep_get_dict(self.data, "Purchase.PurchaseInfo")
            or deep_get_dict(self.data, "PurchaseView.PurchaseInfo")
            or deep_get_dict(self.data, "formData.Purchase.PurchasePanel.PurchaseInfo")
        )

    @property
    def trading_number(self):
        try:
            trading_number = deep_get_dict(
                self.data, "Purchase.PurchaseinfoPanel.PurchaseInfo.PurchaseCode"
            )
            return trading_number
        except Exception as e:
            logger.warning(f"{self.url} th| WITHOUT TRADING NUMBER")
        return None

    @property
    def trading_type_str(self):
        return (
            deep_get_dict(
                self.purchase_info,
                "PurchaseTypeInfo.PurchaseTypeName",
            )
            or deep_get_dict(self.purchase_info, "PurchaseTypeInfo.PurchaseTypeName")
            or deep_get_dict(self.purchase_info, "PurchaseTypeName")
        )

    @property
    def trading_type(self):
        try:
            trading_type = sort_trading_type(self.trading_type_str)
            return trading_type
        except Exception as e:
            logger.warning(f"{self.url} | WITHOUT TRADING TYPE")
        return None

    @property
    def trading_form(self):
        try:
            trading_type = get_trading_form(self.trading_type_str) or "open"
            return trading_type
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA TRADING TYPE", exc_info=True)
        return None

    @property
    def org_info(self):
        return (
            deep_get_dict(self.data, "Purchase.OrganizatorInfo")
            or deep_get_dict(self.data, "Purchase.PurchaseinfoPanel.OrganizatorInfo")
            or deep_get_dict(self.data, "PurchaseView.OrganizatorInfo")
            or deep_get_dict(
                self.data, "formData.Purchase.PurchasePanel.OrganizatorInfo"
            )
        )

    @property
    def trading_org(self):
        try:
            td_org = (
                self.org_info.get("orgname")
                or self.org_info.get("fullName")
                or self.org_info.get("fullname")
            )
            return "".join(re.sub(r"\s+", " ", td_org))
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA ORGANIZER")
        return None

    @property
    def trading_org_inn(self):
        try:
            td_inn = (
                self.org_info.get("INN")
                or self.org_info.get("orginn")
                or self.org_info.get("OrgINN")
            )
            return Contacts.check_inn(td_inn)
        except Exception as e:
            return None

    @property
    def phone(self):
        try:
            phone = (
                self.org_info.get("contactPhone")
                or self.org_info.get("orgphone")
                or self.org_info.get("OrgPhone")
                or self.org_info.get("ContactInfo", {}).get("ContactPhone")
            )
            return Contacts.check_phone(phone)
        except Exception as e:
            return None

    @property
    def email(self):
        try:
            email = (
                self.org_info.get("contactEmail")
                or self.org_info.get("orgemail")
                or self.org_info.get("OrgEmail")
                or self.org_info.get("ContactInfo", {}).get("ContactEmail")
            )
            return Contacts.check_email(email)
        except Exception as e:
            return None

    @property
    def trading_org_contacts(self):
        return {"email": self.email, "phone": self.phone}

    @property
    def msg_number(self):
        try:
            msg_number = deep_get_dict(
                self.data, "Purchase.PurchaseinfoPanel.PurchaseInfo.IDEFRSB"
            )
            return dedent_func(BS(str(msg_number), features="lxml").get_text()).strip()
        except Exception as e:
            return None

    @property
    def case_number(self):
        try:
            case_number = deep_get_dict(
                self.data, "Purchase.DebtorInfo.BusinesInfo.businessno"
            )
            case_number = (
                dedent_func(BS(str(case_number), features="lxml").get_text())
                .replace(";", "")
                .replace("№", "")
                .strip()
            )
            if len(case_number) < 38:
                return case_number.replace("\\", "/").replace(" ", "").strip()
            return None
        except Exception as e:
            return None

    @property
    def debtor_inn(self):
        try:
            td_inn = deep_get_dict(
                self.data, "Purchase.DebtorInfo.DebtorInfo.DebtorINN"
            )
            text_inn = dedent_func(BS(str(td_inn), features="lxml").get_text()).strip()
            return Contacts.check_inn(text_inn)
        except Exception as e:
            return None

    @property
    def address(self):
        try:
            return (
                deep_get_dict(self.data, "Purchase.DebtorInfo.BusinesInfo.businessname")
                or self.org_info.get("postAddress")
                or self.org_info.get("orgaddressjur")
            )
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA ADDRESS DEBITOR")
        return None

    @property
    def arbit_manager(self):
        td_arbitr = deep_get_dict(
            self.data, "Purchase.DebtorInfo.CrisicManagerInfo.crisicmanagerfullname"
        )
        if td_arbitr:
            return td_arbitr
        return None

    @property
    def arbit_manager_inn(self):
        td_inn = deep_get_dict(
            self.data, "Purchase.DebtorInfo.CrisicManagerInfo.crisismanagerinn"
        )
        if td_inn:
            return Contacts.check_inn(td_inn)
        return None

    @property
    def arbitr_manager_org(self):
        td_company = deep_get_dict(
            self.data,
            "Purchase.DebtorInfo.CrisicManagerInfo.arbitrageorganizationpanel.arbitrageorganizationname",
        )
        if td_company:
            return td_company
        return None

    @property
    def start_date_requests(self):
        try:
            return DateTimeHelper.smart_parse(
                deep_get_dict(self.data, "Purchase.Step6.RequestInfo.RequestStartDate")
                or deep_get_dict(self.data, "Purchase.TenderInfo.RequestStartDate")
            ).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA START DATE REQUEST AUCTION")
        return None

    @property
    def end_date_requests(self):
        try:
            return DateTimeHelper.smart_parse(
                deep_get_dict(self.data, "Purchase.Step6.RequestInfo.RequestStopDate")
                or deep_get_dict(self.data, "Purchase.TenderInfo.RequestStopDate")
            ).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA END DATE REQUEST AUCTION")
        return None

    @property
    def start_date_trading(self):
        try:
            return DateTimeHelper.smart_parse(
                deep_get_dict(
                    self.data, "Purchase.Step6.Terms.PurchaseAuctionStartDate"
                )
                or deep_get_dict(self.data, "Purchase.TenderInfo.AuctionStartDate")
            ).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.warning(f"{self.url} | INVALID START DATE TRADING AUCTION")
        return None

    @property
    def end_date_trading(self):
        date = deep_get_dict(self.data, "Purchase.Step6.ResultInfo.AuctionResultDate")
        if not date:
            return None
        return DateTimeHelper.smart_parse(date).astimezone(DateTimeHelper.moscow_tz)

    @property
    def lot_id(self):
        pattern = re.compile(r"\d+$")
        return "".join(pattern.findall(self.url))

    @property
    def lot_link(self):
        return "".join(self.url)

    @property
    def lot_number(self):
        lot_number = deep_get_dict(
            self.data, "BidView.Bids.BidInfo.BidNo"
        ) or deep_get_dict(self.data, "Purchase.Bids.Bid.BidInfo.BidNo")
        return lot_number or "1"

    @property
    def short_name(self):
        short_name = deep_get_dict(
            self.data, "BidView.Bids.BidInfo.BidName"
        ) or deep_get_dict(self.data, "Purchase.Bids.Bid.BidInfo.BidName")
        return short_name

    @property
    def lot_info(self):
        lot_info = deep_get_dict(
            self.data, "BidView.Bids.BidDebtorInfo.DebtorBidName"
        ) or deep_get_dict(self.data, "Purchase.PurchaseInfo.PurchaseName")
        return lot_info

    @property
    def property_information(self):
        property_info = deep_get_dict(
            self.data, "BidView.Bids.BidDebtorInfo.BidInventoryResearchType"
        )
        return property_info

    @property
    def start_price(self):
        start_price = (
            deep_get_dict(self.data, "BidView.Bids.BidTenderInfo.BidPrice")
            or deep_get_dict(self.data, "Purchase.Bids.Bid.BidInfo.BidAmount")
            or deep_get_dict(self.data, "PurchaseView.")
        )
        if start_price:
            return make_float(start_price)
        return None

    @property
    def step_price(self):
        step_price = deep_get_dict(
            self.data, "BidView.Bids.BidTenderInfo.AuctionStepRub"
        )
        if step_price:
            return make_float(step_price)
        return None
