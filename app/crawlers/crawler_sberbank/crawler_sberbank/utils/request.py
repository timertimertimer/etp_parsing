from typing import Callable


class Request:
    def __init__(
        self,
        url: str,
        body: bytes = None,
        headers: dict = None,
        method: str = "GET",
        after_func: Callable = None,
    ):
        self.url = url
        self.headers = headers
        self.method = method
        self.after_func = after_func
        self.body = body
