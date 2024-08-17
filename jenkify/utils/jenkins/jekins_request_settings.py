"""Data class module for Jenkins request settings"""
from dataclasses import dataclass


@dataclass
class JenkinsRequestSettings:
    """Data class for Jenkins request settings"""
    def __init__(self, url: str, auth: tuple, max_retry: int):
        self.url = url
        self.auth = auth
        self.max_retry = max_retry
