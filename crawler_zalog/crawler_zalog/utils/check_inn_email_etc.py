import re


class CheckIfCorrectContactInfo:

    @staticmethod
    def check_phone(phone):
        try:
            if phone:
                match = re.sub(r'\D{3,}', ' ', phone)
                only_numbers = ''.join(filter(lambda x: x.isdigit(), phone))
                if re.match(r'\d{5}', only_numbers) and len(phone) < 50:
                    return match.strip()
        except Exception as e:
            print(e)
            return ''
