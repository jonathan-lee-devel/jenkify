"""Jenkins utilities module"""
from collections.abc import Callable

from requests import Response
from typeguard import typechecked, check_type

from jenkify.enums.http_request_methods import HttpRequestMethod
from jenkify.exceptions.request_retry_exception import RequestRetryException
from jenkify.types.jenkins_responses.rest_api.build_api_json import BuildApiJsonResponse
from jenkify.utils.environment.Environment import Environment
from jenkify.utils.http_request_settings import HttpRequestSettings
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings
from jenkify.utils.json.JsonUtils import JsonUtils
from jenkify.utils.request_retry import request_retry


class JenkinsUtils:
    _jenkins_request_settings: JenkinsRequestSettings
    _get_json_response: Callable[[str, int, HttpRequestSettings], dict | list]

    def __init__(
            self,
            jenkins_request_settings: JenkinsRequestSettings = Environment.get_jenkins_request_settings_from_env(),
            get_json_response: Callable[[str, int, HttpRequestSettings], dict | list] = JsonUtils.get_json_response,
    ):
        self._jenkins_request_settings = jenkins_request_settings
        self._get_json_response = get_json_response

    @staticmethod
    def trim_url_end_option_util(url_end_param: str) -> str:
        """Trims slashes from beginning and end of URL end params"""
        url_end_param = url_end_param.removeprefix('/')
        url_end_param = url_end_param.removesuffix('/')
        return url_end_param

    @typechecked
    def get_jenkins_build_console_output(
            self,
            job_name: str,
            build_number: int) -> str:
        """Jenkins utility function which gets console output for a specific job's build"""
        JsonUtils.validate_max_retry(self._jenkins_request_settings.max_retry)
        return request_retry(HttpRequestMethod.GET,
                             f'{self._jenkins_request_settings.url}/job/{job_name}/{build_number}'
                             '/logText/progressiveText?start=0',
                             self._jenkins_request_settings.max_retry,
                             HttpRequestSettings(auth=self._jenkins_request_settings.auth)).text

    @typechecked
    def get_jenkins_build_console_output_url_end(
            self,
            url_end: str) -> str:
        """Gets console output for a specific job's build based on URL ending"""
        JsonUtils.validate_max_retry(self._jenkins_request_settings.max_retry)
        return request_retry(HttpRequestMethod.GET,
                             f'{self._jenkins_request_settings.url}/{url_end}'
                             '/logText/progressiveText?start=0',
                             self._jenkins_request_settings.max_retry,
                             HttpRequestSettings(auth=self._jenkins_request_settings.auth)
                             ).text

    @typechecked
    def get_jenkins_build_dict(
            self,
            job_name: str,
            build_number: int,
    ) -> BuildApiJsonResponse:
        """Gets Jenkins job JSON data for a specific job's build"""
        JsonUtils.validate_max_retry(self._jenkins_request_settings.max_retry)
        raw_response: dict = self._get_json_response(
            f'{self._jenkins_request_settings.url}/job/{job_name}/{build_number}/api/json',
            self._jenkins_request_settings.max_retry,
            HttpRequestSettings(auth=self._jenkins_request_settings.auth))
        typed_response: BuildApiJsonResponse = check_type(raw_response, BuildApiJsonResponse)
        return typed_response

    @typechecked
    def get_jenkins_build_dict_url_end(
            self,
            url_end: str,
    ) -> dict | None:
        """Gets Jenkins job JSON data for a specific job's build based on URL ending"""
        JsonUtils.validate_max_retry(self._jenkins_request_settings.max_retry)
        try:
            response_dict = self._get_json_response(
                f'{self._jenkins_request_settings.url}/{url_end}/api/json',
                self._jenkins_request_settings.max_retry,
                HttpRequestSettings(auth=self._jenkins_request_settings.auth))
            return response_dict
        except RequestRetryException:
            return None

    @typechecked
    def get_jenkins_build_dict_url_end_build_number(
            self,
            url_end: str,
            build_number: int,
    ) -> dict | None:
        """Gets Jenkins job JSON data based on URL end and build number"""
        JsonUtils.validate_max_retry(self._jenkins_request_settings.max_retry)
        try:
            response_dict = self._get_json_response(
                f'{self._jenkins_request_settings.url}/{url_end}/{build_number}'
                '/api/json',
                self._jenkins_request_settings.max_retry,
                HttpRequestSettings(auth=self._jenkins_request_settings.auth))
            return response_dict
        except RequestRetryException:
            return None

    @typechecked
    def start_jenkins_build(
            self,
            job_name: str,
    ) -> Response:
        """Kicks off a build for specified Jenkins job based on job name"""
        JsonUtils.validate_max_retry(self._jenkins_request_settings.max_retry)
        return request_retry(HttpRequestMethod.POST,
                             f'{self._jenkins_request_settings.url}/job/{job_name}/build?delay=0sec',
                             self._jenkins_request_settings.max_retry,
                             HttpRequestSettings(auth=self._jenkins_request_settings.auth))

    @typechecked
    def start_jenkins_build_url_end(
            self,
            url_end: str,
    ) -> int:
        """Kicks off a build for a specified Jenkins job based on URL ending"""
        JsonUtils.validate_max_retry(self._jenkins_request_settings.max_retry)
        try:
            status_code = request_retry(HttpRequestMethod.POST,
                                        f'{self._jenkins_request_settings.url}/{url_end}/build?delay=0sec',
                                        self._jenkins_request_settings.max_retry,
                                        HttpRequestSettings(auth=self._jenkins_request_settings.auth)
                                        ).status_code
            return status_code
        except RequestRetryException:
            return 500
