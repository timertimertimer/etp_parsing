import re
from .manage_spider import replaceMultiple
import logging

logger = logging.getLogger(__name__)


class CheckIfCorrectContactInfo:
    @staticmethod
    def check_inn(inn):
        pattern = re.compile(r'\d{10,12}$')
        if pattern:
            return ''.join(pattern.findall(inn))
        else:
            return None

    @staticmethod
    def check_phone(phone):
        phone = ''.join(re.split(r'\s', phone))
        match = re.search(r'\d{5}', str(phone).replace('-', ''))
        if match:
            return phone

    @staticmethod
    def check_email(email):
        try:
            if len(email) <= 50:
                if '@' in email:
                    email = re.findall(
                        r'.+\S@\S.+\.\D{2,5}$', email, flags=re.IGNORECASE)
                    if email and len(email) > 0:
                        return ' '.join(email)
                    else:
                        return ''
                else:
                    return ''
        except:
            return ''
