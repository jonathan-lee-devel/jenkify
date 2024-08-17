"""Helper enum for HTTP request methods"""
from enum import Enum


class HttpRequestMethod(Enum):
    """Helper enum for HTTP request methods"""
    GET = 0
    PATCH = 1
    PUT = 2
    POST = 3
    DELETE = 4
