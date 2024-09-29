from .msg_info import MsgInfo
from .msg_page import MessagePage, AnnounceStartTrade, MsgResultTrade, CanceledMsgTrade, ChangeTradeProcedure

class ComboMsg:

    def __init__(self, response_):
        self.response = response_
        # minfo -> common information NOT message page
        self.minfo = MsgInfo(self.response)
        self.mpage = MessagePage(self.response)
        self.announce = AnnounceStartTrade(self.response)
        self.msgresult = MsgResultTrade(self.response)
        self.cancele_msg = CanceledMsgTrade(self.response)
        self.changed_msg = ChangeTradeProcedure(self.response)

