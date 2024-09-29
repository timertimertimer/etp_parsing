import re


class CheckIfCorrectContactInfo:

    @staticmethod
    def check_inn(inn):
        pattern = re.compile(r'\d{10,12}$')
        if pattern:
            return ' '.join(pattern.findall(inn))
        else:
            return None

    @staticmethod
    def check_phone(phone):
        try:
            if phone:
                match = re.sub(r'\D{6,}', ' ', phone)
                match = re.sub(r'\s+', ' ', match)
                return match.strip()
        except Exception as e:
            print(e)
            return ''

    @staticmethod
    def check_email(email):
        try:
            if len(email) <= 50:
                if '@' in email:
                    email = re.findall(
                        r"([a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)", email, flags=re.IGNORECASE)
                    return ' '.join(email)
                else:
                    return ''
        except Exception as e:
            print(e)
            return ''
