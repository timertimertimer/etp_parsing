import re
from typing import Optional

from .logger import logger


class Contacts:
    @staticmethod
    def check_inn(inn: Optional[str] = None):
        if not inn:
            return None
        inn = inn.strip()
        pattern = re.compile(r"\d{10,12}$")
        if pattern:
            return "".join(pattern.findall(inn))
        return None

    @staticmethod
    def check_number(num: Optional[str] = None):
        if not num:
            return None
        num = num.strip()
        match = "".join(re.findall(r"\d+", num))
        if 4 <= len(match) < 12:
            return match
        return None

    @staticmethod
    def check_case_number(case_number: Optional[str] = None):
        if not case_number:
            return None
        case_number = case_number.strip()
        if "от" in case_number:
            case_number = "".join(str(case_number).split("от")[0])
        pattern = re.compile(r"\D{5,}")
        match = pattern.findall(case_number)
        if match and len("".join(match)) > 0:
            match = "".join(match)
            match1 = case_number.replace(match, "").strip()
        else:
            match1 = case_number
        return match1.replace("№", "").strip()

    @staticmethod
    def check_phone(phone: Optional[str] = None):
        if not phone:
            return None
        phone = phone.strip()
        try:
            only_numbers = "".join(filter(lambda x: x.isdigit(), phone))
            if re.match(r"\d{5}", only_numbers) and len(phone) < 55:
                return re.sub(r"\s+", " ", phone).strip().replace('*', '')
            else:
                return ""
        except Exception as e:
            logger.warning(e)
        return None

    @staticmethod
    def check_email(email: Optional[str] = None):
        if not email:
            return None
        email = email.strip()
        try:
            if len(email) <= 50:
                if "@" in email:
                    email = re.findall(
                        r".+\S@\S.+\.\D{2,4}$", email, flags=re.IGNORECASE
                    )
                    return "".join(email).strip()
        except Exception:
            pass
        return None

    @staticmethod
    def check_msg_number(value: Optional[str] = None):
        if not value:
            return None
        value = value.strip()
        try:
            pattern = r"^\d+$"
            match = re.findall(pattern, value.strip())
            if isinstance(match, list) and len(match) > 1:
                v = "".join(match[0])
            else:
                v = "".join(match)
            if len(v) > 0:
                return v.strip()
        except Exception:
            pass
        return None

    @staticmethod
    def check_address(value: Optional[str] = None):
        if not value:
            return None
        value = value.strip()
        return " ".join(value.split())
