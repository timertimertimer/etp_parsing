from .finished_section import FinishSection
from .lot_page import LotPage
from .general_page import GeneralPage
from .download_page import DownloadPage, DocumentGeneral


class Combo:

    def __init__(self, response_):
        self.response = response_
        self.finished = FinishSection(self.response)
        self.lot = LotPage(self.response)
        self.gen = GeneralPage(self.response)
        self.doc = DownloadPage(self.response)
        self.doc_gen = DocumentGeneral(self.response)