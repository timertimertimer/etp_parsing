def return_not_movable_categories():
    return [not_move_sub_homes, not_move_sub_ground, not_move_sub_others,
            not_move_sub_commercial]


not_move_main_category = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:ocLink',
    'javax.faces.partial.execute': 'formMain:catOc:1:ocLink',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:ocLink': 'formMain:catOc:1:ocLink',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': '',
}

not_move_sub_homes = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:subcat1:0:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:subcat1:0:clCategory': 'formMain:catOc:1:subcat1:0:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': ''
}

not_move_sub_ground = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:subcat1:1:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:subcat1:1:clCategory': 'formMain:catOc:1:subcat1:1:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': '',
}

not_move_sub_others = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:subcat1:2:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:subcat1:2:clCategory': 'formMain:catOc:1:subcat1:2:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': ''
}

not_move_sub_commercial = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:subcat1:3:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:subcat1:3:clCategory': 'formMain:catOc:1:subcat1:3:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': ''
}

not_move_sub_homes_form = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:subcat1:0:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:subcat1:0:clCategory': 'formMain:catOc:1:subcat1:0:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'formMain:scmTypeAuctionId_focus': '',
    'formMain:scmSubjectRFId_focus': '',
    'formMain:itKeyWords': '',
    'formMain:itTradeOrganizer': '',
    'formMain:auctionDatePlanBID_input': '',
    'formMain:auctionDatePlanEID_input': '',
    'formMain:costBValueB': '0',
    'formMain:costBValueE': '0',
    'formMain:itLotNoticeNum': '',
    'formMain:itAuctionRegNum': '',
    'formMain:selectIndRightEnsure': '2',
    'formMain:selectIndPublish': '1',
    'javax.faces.ViewState': ''
}

not_move_sub_ground_form = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:subcat1:1:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:subcat1:1:clCategory': 'formMain:catOc:1:subcat1:1:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'formMain:scmTypeAuctionId_focus': '',
    'formMain:scmSubjectRFId_focus': '',
    'formMain:itKeyWords': '',
    'formMain:itTradeOrganizer': '',
    'formMain:auctionDatePlanBID_input': '',
    'formMain:auctionDatePlanEID_input': '',
    'formMain:costBValueB': '0',
    'formMain:costBValueE': '0',
    'formMain:itLotNoticeNum': '',
    'formMain:itAuctionRegNum': '',
    'formMain:selectIndRightEnsure': '2',
    'formMain:selectIndPublish': '1',
    'javax.faces.ViewState': ''
}

not_move_sub_others_form = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:subcat1:2:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:subcat1:2:clCategory': 'formMain:catOc:1:subcat1:2:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'formMain:scmTypeAuctionId_focus': '',
    'formMain:scmSubjectRFId_focus': '',
    'formMain:itKeyWords': '',
    'formMain:itTradeOrganizer': '',
    'formMain:auctionDatePlanBID_input': '',
    'formMain:auctionDatePlanEID_input': '',
    'formMain:costBValueB': '0',
    'formMain:costBValueE': '0',
    'formMain:itLotNoticeNum': '',
    'formMain:itAuctionRegNum': '',
    'formMain:selectIndRightEnsure': '2',
    'formMain:selectIndPublish': '1',
    'javax.faces.ViewState': ''
}

not_move_sub_commercial_form = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:1:subcat1:3:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:1:subcat1:3:clCategory': 'formMain:catOc:1:subcat1:3:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'formMain:scmTypeAuctionId_focus': '',
    'formMain:scmSubjectRFId_focus': '',
    'formMain:itKeyWords': '',
    'formMain:itTradeOrganizer': '',
    'formMain:auctionDatePlanBID_input': '',
    'formMain:auctionDatePlanEID_input': '',
    'formMain:costBValueB': '0',
    'formMain:costBValueE': '0',
    'formMain:itLotNoticeNum': '',
    'formMain:itAuctionRegNum': '',
    'formMain:selectIndRightEnsure': '2',
    'formMain:selectIndPublish': '1',
    'javax.faces.ViewState': ''
}
