from http.cookies import SimpleCookie
from crawler_fabricant.utils.work_with_text_and_number import *
from crawler_fabricant.locators.spider_locators import *
import logging

logger = logging.getLogger(__name__)


###__GET_STATUS_FROM_GRID_ON_SERP_###
def get_status(link):
    return status_loc.format(link)

def get_trading_form(link):
    return trading_form_from_serp.format(link)


##############__________Multiraplace__________#############
def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the sings to be replaced
    for elem in toBeReplaces:
        # Check if string is in the main string
        if elem in mainString:
            # Replace the string
            mainString = mainString.replace(elem, newString)

    return mainString


pattern_replace = ['(', ')', '-', '+', '- ', ' ', ]
pattern_replace1 = ['(', ')', '-', '+', '- ', 'null', '\n', '&nbsp;']

###___WORKING_WITH_COOKIES_SCRAPY_SPLASH_###
def cookie_parser(cookies_string):
    cookie_string = cookies_string
    cookie = SimpleCookie()
    cookie.load(cookie_string)
    cookies = {}
    for key, morsel in cookie.items():
        cookies[key] = morsel.value
    return cookies


###_prepare_request_###
def clean_active(value):
    if value:
        value = dedent_func(value)
        string = re.sub(r'(\d)\s+(\d)', r'\1\2', value)
        string = string.replace(' ', '').strip()
        match = re.findall(r'Приемзаявок\d+', ''.join(string).strip())
        if match:
            match2 = re.findall(r'\d+', str(match).strip())
            return ''.join(match2)
        else:
            return None
    else:
        return None

######___OFFER____#######
def check_name_arbitr(text, url):
    if len(text) < 32:
        for i in ''.join(text):
            if i.isalpha():
                continue
            else:
                logger.warning(f'{url}: CHECK CONTACT INFO OF MEMBERS OF TRADING')
                return None
        return text
    else:
        logger.warning(f'{url}: CHECK CONTACT INFO OF MEMBERS OF TRADING')
        return None

def check_name_org(text,url):
    if text:
        lst_text = re.split(r'\(', text)
        if lst_text:
            return ''.join(lst_text[0])
        else:
            if text < 79:
                for w in text:
                    if w.isapha():
                        continue
                    else:
                        logger.warning(f'{url}: CHECK ORGANIZATOR NAME')
                        return None
                return text
            else:
                logger.warning(f'{url}: CHECK ORGANIZATOR NAME')
                return None


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

#_Working_with_documents_offer_###
#doc lot
def get_lot_tab(text):
    text = dedent_func(text)
    match = re.findall(r'\d+$', text)
    if match:
        return ''.join(match)
    else:
        return None

def amount_of_doc_lot(num: str) -> str:
    return doc_lot_num_loc.format(num)

def tbody_lot_doc(num: str) -> str:
    return tbody_lot_doc_loc.format(num)



