"""Jenkins Job Status enum"""
from enum import Enum


class JenkinsJobStatus(Enum):
    """Jenkins Job Status enum"""
    UNKNOWN = 0
    SUCCESS = 1
    UNSTABLE = 2
    FAILURE = 3
    ABORTED = 4
