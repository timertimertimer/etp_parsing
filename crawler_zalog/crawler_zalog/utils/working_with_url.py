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
    def update_param(url, param_name, param_new_value):
        params = {param_name: param_new_value}

        url_parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)

        url_parts[4] = urllib.parse.urlencode(query)

        url_output = urllib.parse.urlunparse(url_parts)
        return url_output.replace('+', '%20')
