import urllib.parse


class UrlConfig:

    @staticmethod
    def return_parsed_url(url):
        return urllib.parse.urlparse(url)

    @staticmethod
    def return_query_dict(url):
        url_ = urllib.parse.urlparse(url)
        param_dict = urllib.parse.parse_qs(url_.query)
        if param_dict:
            return param_dict

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

    @staticmethod
    def quote_url(url):
        return urllib.parse.quote(url)

    @staticmethod
    def quote_netloc(url):
        url = urllib.parse.urlparse(url)
        url = url.scheme + '://' + urllib.parse.quote(url.netloc)
        return url

    @staticmethod
    def unquote_url(url):
        url = urllib.parse.urlparse(url)
        if len(url.query) > 0:
            url = url.scheme + '://' + urllib.parse.unquote(url.netloc) + urllib.parse.quote(url.path) + f'?{url.query}'
            return url
        elif url.path:
            return url.scheme + '://' + urllib.parse.unquote(url.netloc) + url.path
        else:
            return url.scheme + '://' + urllib.parse.unquote(url.netloc)

    @staticmethod
    def retrun_value_of_param(url, param_key):
        """ :arg url -> receive url
            :arg param_key -> receive key of dictionary that value must be reterned
        """
        parse_url = urllib.parse.urlparse(url)
        params = dict(urllib.parse.parse_qsl(parse_url.query)) if len(parse_url.query) > 0 else None
        return params.get(param_key, None)
        # p = params.setdefault('notificationId', None) if params else None

