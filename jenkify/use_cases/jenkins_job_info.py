"""Jenkins Job Info Module"""
from typeguard import typechecked

from jenkify.enums.jenkins import JenkinsJobStatus
from jenkify.utils.environment.Environment import Environment
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings
from jenkify.utils.jenkins.jenkins_rest_api.jenkins_utils import JenkinsUtils


class JenkinsJobInfoUseCase:
    _jenkins_request_settings: JenkinsRequestSettings
    _jenkins_utils: JenkinsUtils

    def __init__(self,
                 jenkins_request_settings: JenkinsRequestSettings =
                 Environment.get_jenkins_request_settings_from_env(),
                 jenkins_utils: JenkinsUtils = JenkinsUtils(),
                 ):
        self._jenkins_request_settings = jenkins_request_settings
        self._jenkins_utils = jenkins_utils

    @typechecked
    def get_jenkins_job_result_status(
            self,
            url_end: str,
            build_number: int) -> JenkinsJobStatus:
        """Gets the result status of the Jenkins job run"""
        response_dict = self._jenkins_utils.get_jenkins_build_dict_url_end_build_number(
            url_end,
            build_number,
        )
        if response_dict is not None:
            if response_dict['result'] == 'SUCCESS':
                return JenkinsJobStatus.SUCCESS
            if response_dict['result'] == 'UNSTABLE':
                return JenkinsJobStatus.UNSTABLE
        else:
            return JenkinsJobStatus.UNKNOWN

        return JenkinsJobStatus.FAILURE
