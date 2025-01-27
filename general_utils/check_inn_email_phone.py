import re


class CheckIfCorrectContactInfo:

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
                match = re.sub(r'\D{3,}', ' ', phone)
                return match.strip()
        except Exception as e:
            pass

    @staticmethod
    def check_email(email):
        try:
            if len(email) <= 50:
                if '@' in email:
                    email = re.findall(r'.+\S@\S.+\.\D{2,4}$', email, flags=re.IGNORECASE)
                    return ''.join(email)
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
