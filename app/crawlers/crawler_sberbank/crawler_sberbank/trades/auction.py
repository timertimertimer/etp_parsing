import re

from app.utils import dedent_func, Contacts, logger, DateTimeHelper
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
            logger.error(f"{self.url} | INVALID DATA TRADING ID")
        return None

    @property
    def trading_link_auc(self):
        return self.url

    @property
    def trading_number_auc(self):
        try:
            trading_number = deep_get_dict(
                self.data, "Purchase.PurchaseinfoPanel.PurchaseInfo.PurchaseCode"
            )
            return dedent_func(
                BS(str(trading_number), features="lxml").get_text()
            ).strip()
        except Exception as e:
            logger.error(f"{self.url} th| WITHOUT TRADING NUMBER")
        return None

    @property
    def trading_type_auc(self):
        trading_type = sort_trading_type(
            deep_get_dict(
                self.data,
                "Purchase.PurchaseinfoPanel.PurchaseInfo.PurchaseTypeInfo.PurchaseTypeName",
            )
        )
        return trading_type

    @property
    def trading_form_auc(self):
        try:
            trading_type = get_trading_form(
                deep_get_dict(
                    self.data,
                    "Purchase.PurchaseinfoPanel.PurchaseInfo.PurchaseTypeInfo.PurchaseTypeName",
                )
            )
            return dedent_func(
                BS(str(trading_type), features="lxml").get_text()
            ).strip()
        except Exception as e:
            logger.error(f"{self.url} | INVALID DATA TRADING TYPE", exc_info=True)
        return None

    @property
    def trading_org_auc(self):
        try:
            td_org = deep_get_dict(
                self.data, "Purchase.PurchaseinfoPanel.OrganizatorInfo.orgname"
            )
            return "".join(re.sub(r"\s+", " ", td_org))
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA ORGANIZER")
        return None

    @property
    def trading_org_inn(self):
        try:
            td_inn = deep_get_dict(
                self.data, "Purchase.PurchaseinfoPanel.OrganizatorInfo.orginn"
            )
            text_inn = dedent_func(BS(str(td_inn), features="lxml").get_text()).strip()
            return Contacts.check_inn(text_inn)
        except Exception as e:
            return None

    def get_phone_number(self):
        try:
            phone = deep_get_dict(
                self.data,
                "Purchase.PurchaseinfoPanel.OrganizatorInfo.orgphone",
                default="",
            )
            phone = (
                dedent_func(BS(str(phone), features="lxml").get_text())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_phone(phone)
        except Exception as e:
            return None

    def get_email(self):
        try:
            email = deep_get_dict(
                self.data,
                "Purchase.PurchaseinfoPanel.OrganizatorInfo.orgemail",
                default="",
            )
            email = (
                dedent_func(BS(str(email), features="lxml").get_text())
                .replace(";", "")
                .strip()
            )
            return Contacts.check_email(email)
        except Exception as e:
            return None

    @property
    def trading_org_contacts(self):
        if self.get_phone_number():
            phone = self.get_phone_number()
        else:
            phone = None
        if self.get_email():
            email = self.get_email()
        else:
            email = None
        return {"email": email, "phone": phone}

    @property
    def get_msg_number(self):
        try:
            msg_number = deep_get_dict(
                self.data, "Purchase.PurchaseinfoPanel.PurchaseInfo.IDEFRSB"
            )
            return dedent_func(BS(str(msg_number), features="lxml").get_text()).strip()
        except Exception as e:
            return None

    @property
    def get_case_number(self):
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
    def get_debitor_inn(self):
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
            return deep_get_dict(
                self.data, "Purchase.DebtorInfo.BusinesInfo.businessname"
            )
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA ADDRESS DEBITOR")
        return None

    @property
    def get_arbitr_manager(self):
        try:
            td_arbitr = deep_get_dict(
                self.data, "Purchase.DebtorInfo.CrisicManagerInfo.crisicmanagerfullname"
            )
            td_arbitr = dedent_func(
                BS(str(td_arbitr), features="lxml").get_text()
            ).strip()
            return "".join(re.sub(r"\s+", " ", td_arbitr))
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA ARBITR MANAGER NAME")
        return None

    @property
    def get_arbitr_manager_inn(self):
        try:
            td_inn = deep_get_dict(
                self.data, "Purchase.DebtorInfo.CrisicManagerInfo.crisismanagerinn"
            )
            text_inn = dedent_func(BS(str(td_inn), features="lxml").get_text()).strip()
            return Contacts.check_inn(text_inn)
        except Exception as e:
            return None

    @property
    def get_arbitr_manager_org(self):
        try:
            td_company = deep_get_dict(
                self.data,
                "Purchase.DebtorInfo.CrisicManagerInfo.arbitrageorganizationpanel.arbitrageorganizationname",
            )
            td_company = dedent_func(
                BS(str(td_company), features="lxml").get_text()
            ).strip()
            if "(" in td_company:
                td_company = "".join(
                    [
                        x if len(td_company) > 0 else None
                        for x in re.split(r"\(", td_company, maxsplit=1)[0]
                    ]
                )
                return "".join(td_company)
            else:
                return td_company
        except Exception as e:
            return None

    @property
    def get_start_date_requests(self):
        try:
            return DateTimeHelper.smart_parse(
                deep_get_dict(self.data, "Purchase.Step6.RequestInfo.RequestStartDate")
            ).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(f"{self.url} | INVALID DATA START DATE REQUEST AUCTION")
        return None

    @property
    def get_end_date_requests(self):
        try:
            return DateTimeHelper.smart_parse(
                deep_get_dict(self.data, "Purchase.Step6.RequestInfo.RequestStopDate")
            ).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(f"{self.url} | INVALID DATA END DATE REQUEST AUCTION")
        return None

    @property
    def get_start_date_trading(self):
        try:
            return DateTimeHelper.smart_parse(
                deep_get_dict(
                    self.data, "Purchase.Step6.Terms.PurchaseAuctionStartDate"
                )
            ).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(f"{self.url} | INVALID START DATE TRADING AUCTION")
        return None

    @property
    def get_end_date_trading(self):
        try:
            return DateTimeHelper.smart_parse(
                deep_get_dict(self.data, "Purchase.Step6.ResultInfo.AuctionResultDate")
            ).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(f"{self.url} | INVALID END DATE TRADING AUCTION")
        return None

    @property
    def get_lot_id(self):
        pattern = re.compile(r"\d+$")
        return "".join(pattern.findall(self.url))

    @property
    def get_lot_link(self):
        return "".join(self.url)

    @property
    def get_lot_number(self):
        lot_number = deep_get_dict(self.data, "BidView.Bids.BidInfo.BidNo")
        try:
            lot_number = dedent_func(
                BS(str(lot_number), features="lxml").get_text()
            ).strip()
            if int(lot_number):
                return lot_number
        except Exception as e:
            logger.warning(f"{self.url} | INVALID DATA LOT NUMBER")
        return "1"

    @property
    def get_short_name(self):
        short_name = deep_get_dict(self.data, "BidView.Bids.BidInfo.BidName")
        try:
            short_name = dedent_func(
                BS(str(short_name), features="lxml").get_text()
            ).strip()
            if short_name:
                return short_name
            return None
        except Exception as e:
            return None

    @property
    def get_lot_info(self):
        lot_info = deep_get_dict(self.data, "BidView.Bids.BidDebtorInfo.DebtorBidName")
        try:
            lot_info = dedent_func(
                BS(str(lot_info), features="lxml").get_text()
            ).strip()
            if lot_info:
                return lot_info
            return None
        except Exception as e:
            return None

    @property
    def get_property_info(self):
        property_info = deep_get_dict(
            self.data, "BidView.Bids.BidDebtorInfo.BidInventoryResearchType"
        )
        try:
            property_info = dedent_func(
                BS(str(property_info), features="lxml").get_text()
            ).strip()
            if property_info:
                return property_info
            return None
        except Exception as e:
            return None

    @property
    def get_start_price(self):
        start_price = deep_get_dict(self.data, "BidView.Bids.BidTenderInfo.BidPrice")
        start_price = re.sub(r"\s", "", start_price)
        pattern = re.compile(r"\d+\.\d{1,2}")
        try:
            start_price = dedent_func(
                BS(str(start_price), features="lxml").get_text()
            ).strip()
            if start_price:
                return round(float("".join(pattern.findall(start_price)[0])), 2)
        except Exception as e:
            logger.error(f"{self.url} | INVALID DATA START PRICE AUCTION")
        return None

    @property
    def get_step_price(self):
        step_price = deep_get_dict(
            self.data, "BidView.Bids.BidTenderInfo.AuctionStepRub"
        )
        step_price = re.sub(r"\s", "", step_price)
        pattern = re.compile(r"\d+\.\d{1,2}")
        pattern1 = re.compile(r"^\d{1,2}")
        try:
            step_price = dedent_func(
                BS(str(step_price), features="lxml").get_text()
            ).strip()
            step_price = "".join(pattern.findall(step_price))
            if step_price:
                step_price = round(float(step_price), 2)
            else:
                step_price = "".join(pattern1.findall(step_price))
                step_price = round(float(step_price), 2)
            return round(float(self.get_start_price * (step_price / 100)), 2)
        except Exception as e:
            logger.error(f"{self.url} | INVALID DATA STEP PRICE AUCTION")
        return None
