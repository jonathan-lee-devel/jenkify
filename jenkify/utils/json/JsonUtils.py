from jenkify.enums.http_request_methods import HttpRequestMethod
from jenkify.utils.http_request_settings import HttpRequestSettings
from jenkify.utils.request_retry import request_retry


class JsonUtils:
    @staticmethod
    def validate_max_retry(max_retry: int) -> None:
        """Validates max retry parameter"""
        if max_retry < 1 or max_retry > 100_000:
            raise ValueError('Max retry value invalid')

    @staticmethod
    def get_json_response(
            url: str,
            max_retry: int,
            http_request_settings: HttpRequestSettings,
    ) -> dict | list:
        """Common util function which gets JSON response as dict"""
        JsonUtils.validate_max_retry(max_retry)
        return (request_retry(HttpRequestMethod.GET,
                              url,
                              max_retry,
                              http_request_settings)
                .json())
