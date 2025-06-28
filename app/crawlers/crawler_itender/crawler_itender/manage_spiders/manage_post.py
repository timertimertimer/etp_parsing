from bs4 import BeautifulSoup as BS

from app.utils.logger import logger


class ManagePost:
    def __init__(self, response):
        self.response = response
        self.soup = BS(
            str(self.response.body.decode("utf-8"))
            .replace("&lt;", "<")
            .replace("&gt;", ">"),
            features="lxml",
        )

    def get_post_data_values(self, tag_html: str, post_argument: str) -> str or None:
        try:
            tag_html = self.soup.find(tag_html, id=post_argument)
            if tag_html:
                tag_html = tag_html["value"]
                return tag_html
            else:
                return ""
        except Exception as e:
            logger.warning(f" :: Exeption during fetching tag {tag_html} :: {e} ")
            return ""
