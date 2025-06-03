import re
import logging

logger = logging.getLogger(__name__)


class Contacts:

    @staticmethod
    def check_inn(inn):
        pattern = re.compile(r'\d{10,12}$')
        if pattern:
            return ''.join(pattern.findall(inn))

    @staticmethod
    def check_number(num):
        match = ''.join(re.findall(r'\d+', num))
        if 4 <= len(match) < 12:
            return match
        else:
            return None

    @staticmethod
    def check_case_number(case_number: str or None):
        if case_number:
            # find if 4 characters are inline together
            if 'от' in case_number:
                case_number = ''.join(str(case_number).split('от')[0])
            pattern = re.compile(r'\D{5,}')
            match = pattern.findall(case_number)
            if match and len(''.join(match)) > 0:
                match = ''.join(match)
                match1 = case_number.replace(match, '').strip()
            else:
                match1 = case_number
            return match1.replace('№', '').strip()

    @staticmethod
    def check_phone(phone):
        try:
            if phone:
                only_numbers = ''.join(filter(lambda x: x.isdigit(), phone))
                if re.match(r'\d{5}', only_numbers) and len(phone) < 55:
                    return re.sub(r'\s+', ' ', phone).strip()
                else:
                    return ''
        except Exception as e:
            logger.error(e)

    @staticmethod
    def check_email(email):
        try:
            if len(email) <= 50:
                if '@' in email:
                    email = re.findall(r'.+\S@\S.+\.\D{2,4}$', email, flags=re.IGNORECASE)
                    return ''.join(email).strip()
        except Exception as e:
            pass

    @staticmethod
    def check_msg_number(value):
        try:
            if value:
                pattern = r'^\d+$'
                match = re.findall(pattern, value.strip())
                if type(match) == list and len(match) > 1:
                    v = ''.join(match[0])
                else:
                    v = ''.join(match)
                if len(v) > 0:
                    return v.strip()
                else:
                    return
        except Exception as e:
            pass

    @staticmethod
    def check_address(value):
        try:
            if value:
                return ' '.join(value.split())
        except Exception as e:
            pass
