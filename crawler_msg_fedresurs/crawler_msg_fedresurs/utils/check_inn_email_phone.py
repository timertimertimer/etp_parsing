import re


class CheckIfCorrectContactInfo:

    @staticmethod
    def check_inn(inn):
        pattern = re.compile(r'\d{10,12}$')
        if pattern:
            return ''.join(pattern.findall(inn))
        else:
            return None

    @staticmethod
    def check_number(num):
        match = ''.join(re.findall(r'\d+', num))
        if 4 < len(match) < 9:
            return match
        else:
            return None

    @staticmethod
    def check_case_number(case_number: str or None):
        if case_number:
            # find if 4 characters are inline together
            pattern = re.compile('\D{5,}')
            match = pattern.findall(case_number)
            if match and len(''.join(match)) > 0:
                match = ''.join(match)
                match1 = case_number.replace(match, '').strip()
            else:
                match1 = case_number
            return match1.replace('№', '').strip()

    @staticmethod
    def check_phone(phone):
        return phone

    @staticmethod
    def check_email(email):
        try:
            if len(email) <= 50:
                if '@' in email:
                    email = re.findall(
                        r'.+\S@\S.+\.\D{2,4}$', email, flags=re.IGNORECASE)
                    return ''.join(email)
                else:
                    return ''
        except:
            return ''
