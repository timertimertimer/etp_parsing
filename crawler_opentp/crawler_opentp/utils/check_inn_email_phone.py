import re


class CheckIfCorrectContactInfo:

    def check_inn(self, inn):
        pattern = re.compile(r'\d{10,12}$')
        return ''.join(pattern.findall(inn))

    def check_phone(self, phone):
        phone = ''.join(re.split(r'\s', phone))
        match = re.search(r'\d{5}', str(phone).replace('-', ''))
        if match:
            return phone

    def check_email(self, email):
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
