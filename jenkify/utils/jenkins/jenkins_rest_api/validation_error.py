"""YAML/Dictionary validation error data class module"""
from dataclasses import dataclass


@dataclass
class ValidationError:
    """YAML/Dictionary validation error data class"""
    def __init__(self, field: str, message: str):
        self.field = field
        self.message = message
