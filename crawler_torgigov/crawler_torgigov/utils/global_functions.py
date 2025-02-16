from ..utils.config import start_date, end_date
from ..utils.param_data_search.param_finished import param_finished as pf
from ..utils.param_data_search.param_finished import param_finished_form as pff
from ..utils.param_data_search.param_government import param_search_government as psg
from ..utils.param_data_search.param_government import param_gover_extend_form as pge


class GlobalFeatures:

    def __init__(self, section, date_from, date_to):
        self.section = section
        self.date_from = date_from
        self.date_to = date_to

    def __repr__(self):
        return f'{self.section}, {self.date_from}, {self.date_to}'

    def choose_parse_section(self):
        """ return url of parsing """
        if self.section == 'finished':
            return 'https://torgi.gov.ru/lotSearch5.html'
        elif self.section == 'pending':
            return 'https://torgi.gov.ru/lotSearch3.html'
        elif self.section == 'canceled':
            return 'https://torgi.gov.ru/lotSearch4.html'
        elif self.section == 'stoped':
            return 'https://torgi.gov.ru/lotSearch6.html'
        elif self.section == 'archived':
            return 'https://torgi.gov.ru/lotSearchArchive.html'
        elif self.section == 'active':
            return 'https://torgi.gov.ru/lotSearch2.html'

    def param_data_for_parsing(self):
        """ according link of parsing choose params for request """
        link: str = self.choose_parse_section()
        lst = ['lotSearch2', 'lotSearch3', 'lotSearch4', 'lotSearch5', 'lotSearch6', 'lotSearchArchive']
        if any(x in link for x in lst):
            return pf

    @staticmethod
    def param_data_for_parsing_gov():
        return psg

    def param_data_extended_form(self):
        """ according link of parsing choose params for activate extended form """
        link: str = self.choose_parse_section()
        lst = ['lotSearch2', 'lotSearch3', 'lotSearch4', 'lotSearch5', 'lotSearch6', 'lotSearchArchive']
        if any(x in link for x in lst):
            return pff

    @staticmethod
    def param_data_extended_form_government():
        """ param_data_extended_form_government """
        return pge

    def date_from_func(self):
        """ :return date from - filter data. If arg date from is None take date from config file """
        if self.date_from == '':
            return str(start_date)
        else:
            return self.date_from

    def date_to_func(self):
        """ :return date to - filter data. If arg date to don't use it """
        return self.date_to if self.date_to != '' else end_date
