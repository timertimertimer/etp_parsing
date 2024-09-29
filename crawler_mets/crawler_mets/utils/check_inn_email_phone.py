import re
from .manage_spider import replaceMultiple


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
