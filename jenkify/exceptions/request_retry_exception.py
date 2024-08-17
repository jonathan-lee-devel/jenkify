"""Request retry exceptions module"""


class RequestRetryException(Exception):
    """Default request retry exception"""

    def __init__(self, message=None):
        self.message = message
        super().__init__(self.message)
