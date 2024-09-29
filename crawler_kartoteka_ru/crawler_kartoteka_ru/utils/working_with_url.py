import urllib.parse


class UrlConfig:

    @staticmethod
    def parse_url(url):
        url = urllib.parse.urlparse(url)
        if len(url.query) > 0:
            url = url.scheme + '://' + url.netloc + urllib.parse.quote(url.path) + f'?{url.query}'
        else:
            url = url.scheme + '://' + url.netloc + urllib.parse.quote(url.path)
        return url

    @staticmethod
    def return_netloc(url):
        return urllib.parse.urlparse(url).netloc

    @staticmethod
    def return_url_param(url, param):
        return url + f'?{urllib.parse.urlencode(param)}'

    @staticmethod
    def url_join(main_url, link):
        return urllib.parse.urljoin(main_url, link)