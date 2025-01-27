import re
from .spider_manage import replaceMultiple


class CheckIfCorrectContactInfo:

    def check_inn(self, inn):
        pattern = re.compile(r'\d{10,12}$')
        return ''.join(pattern.findall(inn))

    def check_phone(self, phone):
        return phone


    def check_email(self, email):
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
