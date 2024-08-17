"""Data class module for HTTP request settings"""
from dataclasses import dataclass


@dataclass
class HttpRequestSettings:
    """Data class for HTTP request settings"""
    def __init__(
            self,
            body: dict | None = None,
            proxy: dict | None = None,
            ssl: bool = False,
            auth: tuple = None
    ):
        self.body = body
        self.proxy = proxy
        self.ssl = ssl
        self.auth = auth
