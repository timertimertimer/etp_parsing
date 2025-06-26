import urllib.parse


class URL:
    @staticmethod
    def parse_url(url):
        url = urllib.parse.urlparse(url)
        if len(url.query) > 0:
            url = (
                url.scheme
                + "://"
                + url.netloc
                + urllib.parse.quote(url.path)
                + f"?{url.query}"
            )
        else:
            url = url.scheme + "://" + url.netloc + urllib.parse.quote(url.path)
        return url

    @staticmethod
    def check_url_scheme(url):
        url = urllib.parse.urlparse(url)
        if url.scheme:
            return url
        else:
            return None

    @staticmethod
    def return_netloc(url):
        return urllib.parse.urlparse(url).netloc

    @staticmethod
    def return_only_param(url):
        url = urllib.parse.urlparse(url)
        if len(url.query) > 0:
            return "".join(url.query)

    @staticmethod
    def return_url_param(url, param):
        return url + f"?{urllib.parse.urlencode(param)}"

    @staticmethod
    def url_join(main_url, link):
        return urllib.parse.urljoin(main_url, link)

    @staticmethod
    def quote_url(url):
        return urllib.parse.quote(url)

    @staticmethod
    def quote_netloc(url):
        url = urllib.parse.urlparse(url)
        url = url.scheme + "://" + urllib.parse.quote(url.netloc)
        return url

    @staticmethod
    def unquote_url(url):
        url = urllib.parse.urlparse(url)
        if len(url.query) > 0:
            url = (
                url.scheme
                + "://"
                + urllib.parse.unquote(url.netloc)
                + urllib.parse.quote(url.path)
                + f"?{url.query}"
            )
            return url
        elif url.path:
            return url.scheme + "://" + urllib.parse.unquote(url.netloc) + url.path
        else:
            return url.scheme + "://" + urllib.parse.unquote(url.netloc)

    @staticmethod
    def clean_url(url):
        parsed_url = urllib.parse.urlparse(url)
        return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"

    @staticmethod
    def update_param(url, param_name, param_new_value):
        params = {param_name: param_new_value}

        url_parts = list(urllib.parse.urlparse(url))
        query = dict(urllib.parse.parse_qsl(url_parts[4]))
        query.update(params)

        url_parts[4] = urllib.parse.urlencode(query)

        url_output = urllib.parse.urlunparse(url_parts)
        return url_output.replace("+", "%20")
