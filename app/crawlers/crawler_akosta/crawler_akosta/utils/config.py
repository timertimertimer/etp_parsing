from app.utils.config import (
    absolute_download_path,
    relative_download_path,
)
from app.db.models import AuctionProperty

host = "www.akosta.info"
data_origin = "https://www.akosta.info/"
search_link = "https://www.akosta.info/akosta/lots.xhtml"

common_link = "https://www.akosta.info/akosta/auctionCard.xhtml"
debtor_link = "https://www.akosta.info/akosta/auctionCardDeb.xhtml"
lot_link = "https://www.akosta.info/akosta/auctionCardLots.xhtml"
_link_post_period = "https://www.akosta.info/akosta/lotCard.xhtml"

absolute_path = absolute_download_path / "etp_akosta"
relative_path = relative_download_path / "etp_akosta"

auction_property_type_number_map = {
    AuctionProperty.bankruptcy: 3,
    AuctionProperty.arrested: 4,
}