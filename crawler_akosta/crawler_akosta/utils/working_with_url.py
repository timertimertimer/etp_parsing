# -*- coding: utf-8 -*-
import urllib.parse


class UrlConfig:

    @staticmethod
    def parse_url(url):
        url = urllib.parse.urlparse(url)
        if len(url.query) > 0:
            url = url.scheme + '://' + url.netloc + \
                  urllib.parse.quote(url.path) + f'?{url.query}'
        else:
            url = url.scheme + '://' + url.netloc + \
                  urllib.parse.quote(url.path)
        return url

    @staticmethod
    def return_only_param(url):
        url = urllib.parse.urlparse(url)
        if len(url.query) > 0:
            return ''.join(url.query)

    @staticmethod
    def return_url_param(url, param):
        return url + f'?{urllib.parse.urlencode(param)}'

    @staticmethod
    def url_join(main_url, link):
        return urllib.parse.urljoin(main_url, link)

    @staticmethod
    def make_url_quote(string):
        """encode string to Url-encode(%20)"""
        return urllib.parse.quote(string, encoding='utf-8').lower()

    @staticmethod
    def make_url_unquote(string):
        """encode string to Url-encode(%20)"""
        return urllib.parse.unquote(string, encoding='utf-8')