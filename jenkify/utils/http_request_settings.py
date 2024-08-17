"""Data class module for HTTP request settings"""
from dataclasses import dataclass


@dataclass
class HttpRequestSettings:
    """Data class for HTTP request settings"""

    def __init__(
            self,
            content_type: str = 'application/json',
            body: dict | None = None,
            data: dict | None = None,
            proxy: dict | None = None,
            ssl: bool = False,
            auth: tuple = None
    ):
        self.content_type = content_type
        self.body = body
        self.data = data
        self.proxy = proxy
        self.ssl = ssl
        self.auth = auth
