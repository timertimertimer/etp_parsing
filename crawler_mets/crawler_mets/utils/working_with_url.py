import urllib.parse


class UrlConfig:
    def parse_url(self, url):
        url = urllib.parse.urlparse(url)
        if len(url.query) > 0:
            url = url.scheme + '://' + url.netloc + \
                urllib.parse.quote(url.path) + f'?{url.query}'
        else:
            url = url.scheme + '://' + url.netloc + \
                urllib.parse.quote(url.path)
        return url

    def return_url_param(self, url, param):
        return url + f'?{urllib.parse.urlencode(param)}'

    @staticmethod
    def url_join(main_url, link):
        return urllib.parse.urljoin(main_url, link)
