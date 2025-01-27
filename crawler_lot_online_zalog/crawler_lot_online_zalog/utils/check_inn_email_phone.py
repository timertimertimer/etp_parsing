import re
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
        try:
            if phone:
                only_numbers = ''.join(filter(lambda x: x.isdigit(), phone))
                if re.match(r'\d{5}', only_numbers) and len(phone) < 55:
                    return re.sub(r'\s+', ' ', phone)
                else:
                    return ''
        except Exception as e:
            print(e)
            return ''

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