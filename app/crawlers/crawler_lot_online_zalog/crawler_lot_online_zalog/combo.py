import os
import re
from pathlib import Path

from bs4 import BeautifulSoup as BS

from app.utils import (
    dedent_func,
    DateTimeHelper,
    make_float,
    Contacts, logger,
)
from app.utils.config import image_formats
from app.db.models import DownloadData


class Combo:
    def __init__(self, response):
        self.response = response
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    def get_short_name(self):
        short_name = self.soup.find("div", class_="object-info__title")
        if short_name:
            return dedent_func(short_name.get_text().strip())
        else:
            logger.error(f"{self.response.url} :: ERROR SHORT NAME NOT FOUND")
        return None

    def return_all_scripts(self):
        phone_script = self.soup.find_all("script")
        return phone_script

    def get_phone(self):
        try:
            phone_script = self.return_all_scripts()
            for s in phone_script:
                if "function byPhoneView()" in str(s):
                    phone = re.findall(r"<p><span.+Телефон:(.+)</span>", str(s))
                    if phone:
                        phone = "".join(phone).strip()
                        return Contacts.check_phone(phone)
            return ""
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR WITH PHONE NUMBER\n{e}", exc_info=True
            )
        return None

    def get_trading_org_contact(self):
        return {"email": "", "phone": self.get_phone()}

    def get_trading_id(self):
        try:
            trading_id = self.return_all_scripts()
            for s in trading_id:
                if "window.collateralId" in str(s):
                    trading_id = re.findall(r"\d+", str(s))
                    if len(trading_id) == 1:
                        return "".join(trading_id)
            logger.error(f"{self.response.url} :: ERROR TRADING ID NOT FOUND")
        except Exception as e:
            logger.error(f"{self.response.url} :: ERROR TRADING ID\n{e}")
        return None

    @property
    def address(self):
        try:
            addr = self.soup.find(
                "td", string=re.compile(r"\s?Адрес:\s?", re.IGNORECASE)
            )
            if addr:
                return dedent_func(
                    " ".join(addr.findNext("td").get_text(strip=True).split())
                )
        except Exception as e:
            logger.error(f"{self.response.url} :: ERROR ADDRESS\n{e}")
        return None

    def get_encumbrance(self):
        span = self.soup.find(
            "span", string=re.compile("Вид ограничения:", re.IGNORECASE)
        )
        if span:
            div = dedent_func(span.parent.get_text().strip())
            div_text = re.split(":", div, maxsplit=1)[-1]
            return dedent_func(div_text.strip())
        return None

    def get_description_encumbrance(self):
        h5 = self.soup.find(
            "h5", string=re.compile("Описание обременения:", re.IGNORECASE)
        )
        if h5:
            div = dedent_func(h5.parent.get_text().strip())
            div = re.sub(r":\s{2,}", ": ", div)
            div_text = re.sub(r"\s{2,}", os.linesep, div)
            return div_text.strip()
        return None

    def get_categories(self):
        try:
            div_category = self.soup.find(
                "span", string=re.compile(r"\s?Вид имущества:\s?", re.IGNORECASE)
            )
            if div_category:
                parent_div = div_category.parent
                text = parent_div.get_text().strip()
                text_cat = re.split(":", text, maxsplit=1)[-1]
                text_cat = re.sub(r"\s+", " ", text_cat.replace("\n", " "))
                return [text_cat.strip()]
        except Exception as ex:
            logger.error(f"{self.response.url} :{ex}: ERROR CATEGORY", exc_info=True)
        return None

    def start_date_requests(self):
        try:
            start_date_requests = self.soup.find(
                "div", string=re.compile(r"\s?Дата публикации:\s?", re.IGNORECASE)
            )
            if start_date_requests:
                start_date_requests = (
                    start_date_requests.findNext("div").get_text().strip()
                )
                return DateTimeHelper.smart_parse(start_date_requests).astimezone(DateTimeHelper.moscow_tz)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR START DATE REQUEST or TRADING\n{e}"
            )
        return None

    def start_price(self):
        try:
            start_price = (
                self.soup.find("div", class_="object-sidebar__price")
                .findNext("span")
                .get_text()
                .strip()
            )
            return make_float(start_price)
        except Exception as e:
            logger.error(
                f"{self.response.url} :: ERROR START PRICE\n{e}", exc_info=True
            )
        return None

    def return_complete_lot_info(self):
        if self.check_tab_transport():
            if d := self.get_lot_info_description():
                return self.get_lot_info_characteristic() + os.linesep + d
            else:
                h5 = self.soup.find("h5", string=re.compile("Описание:", re.IGNORECASE))
                try:
                    text = dedent_func(h5.findNext().get_text().strip())
                except Exception as e:
                    print(e)
                    text = ""
                return self.get_lot_info_characteristic() + os.linesep + text
        else:
            if d := self.get_lot_info_description():
                return d
            else:
                h5 = self.soup.find("h5", string=re.compile("Описание:", re.IGNORECASE))
                try:
                    text = dedent_func(h5.findNext().get_text().strip())
                except Exception as e:
                    print(e)
                    text = None
                return text

    def get_lot_info_description(self):
        try:
            detailed = self.soup.find("div", class_="detailed")
            if detailed:
                d = dedent_func(detailed.get_text().strip())
                return re.sub(r"\xa0 Cкрыть детали", "", d).strip()
            elif lot_info := self.soup.find("div", class_="summary"):
                d = dedent_func(detailed.get_text().strip())
                return re.sub(r"\xa0 Cкрыть детали", "", d).strip()
        except Exception as e:
            logger.error(f"{self.response.url} :: Error with LOT INFO\n{e}")
        return None

    def check_tab_transport(self):
        if description_tabs := self.soup.find_all(
            "div", class_=re.compile("object-tabs-controls__item")
        ):
            search_tab = "Транспорт"
            tab_text = [t.get_text().strip() for t in description_tabs]
            return True if search_tab in tab_text else None
        return None

    def get_lot_info_characteristic(self):
        string = ""
        search_words = [
            "Год выпуска:",
            "Марка:",
            "Модель:",
            "Модификация:",
            "Состояние объекта:",
            "Цвет",
            "Пробег",
            "VIN:",
        ]
        year = self.soup.find(
            "span", string=re.compile(r"\s?Год выпуска:\s?", re.IGNORECASE)
        )
        if year:
            parent_div = year.parent
            text = dedent_func(parent_div.get_text().strip())
            if len(text) > 0:
                string += re.sub(r"\s+", " ", text.strip()) + os.linesep
        brand = self.soup.find(
            "span", string=re.compile(r"\s?Марка:\s?", re.IGNORECASE)
        )
        if brand:
            parent_div = brand.parent
            text = dedent_func(parent_div.get_text().strip())
            if len(text) > 0:
                string += re.sub(r"\s+", " ", text.strip()) + os.linesep
        model = self.soup.find(
            "span", string=re.compile(r"\s?Модель:\s?", re.IGNORECASE)
        )
        if model:
            parent_div = model.parent
            text = dedent_func(parent_div.get_text().strip())
            if len(text) > 0:
                string += re.sub(r"\s+", " ", text.strip()) + os.linesep
        modification = self.soup.find(
            "span", string=re.compile(r"\s?Модификация:\s?", re.IGNORECASE)
        )
        if modification:
            parent_div = modification.parent
            text = dedent_func(parent_div.get_text().strip())
            if len(text) > 0:
                string += re.sub(r"\s+", " ", text.strip()) + os.linesep
        condition = self.soup.find(
            "span", string=re.compile(r"\s?Состояние объекта:\s?", re.IGNORECASE)
        )
        if condition:
            parent_div = condition.parent
            text = dedent_func(parent_div.get_text().strip())
            if len(text) > 0:
                string += re.sub(r"\s+", " ", text.strip()) + os.linesep
        color = self.soup.find("span", string=re.compile(r"\s?Цвет:\s?", re.IGNORECASE))
        if color:
            parent_div = color.parent
            text = dedent_func(parent_div.get_text().strip())
            if len(text) > 0:
                string += re.sub(r"\s+", " ", text.strip()) + os.linesep
        mileage = self.soup.find(
            "span", string=re.compile(r"\s?Пробег:\s?", re.IGNORECASE)
        )
        if mileage:
            parent_div = mileage.parent
            text = dedent_func(parent_div.get_text().strip())
            if len(text) > 0:
                string += re.sub(r"\s+", " ", text.strip()) + os.linesep
        vin = self.soup.find("span", string=re.compile(r"\s?VIN:\s?", re.IGNORECASE))
        if vin:
            parent_div = vin.parent
            text = dedent_func(parent_div.get_text().strip())
            if len(text) > 0:
                string += re.sub(r"\s+", " ", text.strip()) + os.linesep

        return string

    def property_info(self):
        try:
            span_property = self.soup.find(
                "span",
                string=re.compile(r"\s?Ознакомление с имуществом:\s?", re.IGNORECASE),
            )
            if span_property:
                return span_property.findNext().get_text().strip()
        except Exception as e:
            logger.error(f"{self.response.url} :: ERROR PROPERTY INFORMATION\n{e}")
        return None

    def get_all_pictures_link(self):
        galary_section = self.soup.find("div", class_="gallery")
        lst_files = list()
        if galary_section:
            _a_lst = galary_section.find_all("a")
            for href in _a_lst:
                lst_files.append("https:" + href.get("href"))
            return list(set(lst_files))
        else:
            return []

    def download_img(self, lst_pictures: list):
        files = list()
        if len(lst_pictures) == 0:
            return files
        for i, pic in enumerate(lst_pictures):
            _sufix = Path(pic).suffix
            if _sufix.lower() in image_formats:
                name = "".join(Path(pic).name).strip()
                files.append(
                    DownloadData(url=pic, file_name=name, referer=self.response.url, is_image=True, order=i)
                )
        return files
