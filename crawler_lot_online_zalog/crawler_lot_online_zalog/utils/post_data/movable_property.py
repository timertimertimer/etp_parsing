def return_movable_sub_categories():
    return [move_sub_equipment_with_form, move_sub_others_with_form, move_sub_cars_with_form]


move_main_category = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:0:ocLink',
    'javax.faces.partial.execute': 'formMain:catOc:0:ocLink',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:0:ocLink': 'formMain:catOc:0:ocLink',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': '',
}

move_sub_equipment = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:0:subcat1:0:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:0:subcat1:0:clCategory': 'formMain:catOc:0:subcat1:0:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': ''
}

move_sub_others = {

    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:0:subcat1:1:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:0:subcat1:1:clCategory': 'formMain:catOc:0:subcat1:1:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': ''
}

move_sub_cars = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:0:subcat1:2:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:0:subcat1:2:clCategory': 'formMain:catOc:0:subcat1:2:clCategory',
    'formMain': 'formMain',
    'formMain:inputServerTime': '',
    'formMain:commonSearchCriteriaStr': '',
    'javax.faces.ViewState': ''

}

move_sub_equipment_with_form = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:0:subcat1:0:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:0:subcat1:0:clCategory': 'formMain:catOc:0:subcat1:0:clCategory',
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

move_sub_others_with_form = {
    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:0:subcat1:1:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:0:subcat1:1:clCategory': 'formMain:catOc:0:subcat1:1:clCategory',
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

move_sub_cars_with_form = {

    'javax.faces.partial.ajax': 'true',
    'javax.faces.source': 'formMain:catOc:0:subcat1:2:clCategory',
    'javax.faces.partial.execute': '@all',
    'javax.faces.partial.render': 'formMain:formCategoriesTree formMain:panelList formMain:LotListPaginatorID formMain:pgFilterFields',
    'formMain:catOc:0:subcat1:2:clCategory': 'formMain:catOc:0:subcat1:2:clCategory',
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
