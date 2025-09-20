from app.db.models import AuctionPropertyType

host = "www.akosta.info"
data_origin = "https://www.akosta.info/"
search_link = "https://www.akosta.info/akosta/lots.xhtml"

common_link = "https://www.akosta.info/akosta/auctionCard.xhtml"
debtor_link = "https://www.akosta.info/akosta/auctionCardDeb.xhtml"
lot_link = "https://www.akosta.info/akosta/auctionCardLots.xhtml"
link_post_period = "https://www.akosta.info/akosta/lotCard.xhtml"

property_type_number = {
    AuctionPropertyType.bankruptcy: 3,
    AuctionPropertyType.arrested: 4,
    AuctionPropertyType.commercial: 5,
}

urls = {
    "akosta_bankruptcy": f"https://www.akosta.info/akosta/lots.xhtml?sgUnid={property_type_number[AuctionPropertyType.bankruptcy]}",
    "akosta_arrested": f"https://www.akosta.info/akosta/lots.xhtml?sgUnid={property_type_number[AuctionPropertyType.arrested]}",
    "akosta_commercial": f"https://www.akosta.info/akosta/lots.xhtml?sgUnid={property_type_number[AuctionPropertyType.commercial]}",
}

post_headers = {
    'Accept': 'application/xml, text/xml, */*; q=0.01',
    'origin': 'https://www.akosta.info',
    'faces-request': 'partial/ajax',
    'x-requested-with': 'XMLHttpRequest',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-origin',
}

# https://www.akosta.info/akosta/javax.faces.resource/dynamiccontent.properties.xhtml?
# ln=primefaces&
# v=6.2&
# pfdrid=745c8f5d986e089f26d8e13ef97a293c&
# pfdrt=sc&
# pictureDfPreviewFilePath=%5C20240506%5Ctmp-6861335255386914639.jpg&
# pictureDfFilePath=%5C20240506%5Ctmp-6861335255386914639.jpg&
# pictureDfExt=jpg&
# pictureDfName=2.jpg&
# pictureWidth=250&
# pfdrid_c=true
