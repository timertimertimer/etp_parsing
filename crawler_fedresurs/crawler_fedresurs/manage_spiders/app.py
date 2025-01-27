from .arbitor import Arbitor
from .org_company import OrgCompany


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.arbitr = Arbitor(self.response)
        self.orgcomp = OrgCompany(self.response)
