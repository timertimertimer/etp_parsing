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
    "akosta_bankrupt": f"https://www.akosta.info/akosta/lots.xhtml?sgUnid={property_type_number[AuctionPropertyType.bankruptcy]}",
    "akosta_arrested": f"https://www.akosta.info/akosta/lots.xhtml?sgUnid={property_type_number[AuctionPropertyType.arrested]}",
    "akosta_commercial": f"https://www.akosta.info/akosta/lots.xhtml?sgUnid={property_type_number[AuctionPropertyType.commercial]}",
}
