"""wfapi runs endpoints utilities module"""
from typeguard import typechecked

from jenkify.utils.http_request_settings import HttpRequestSettings
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings
from jenkify.utils.json.JsonUtils import JsonUtils


@typechecked
def get_job_runs_response_content(
        request_settings: JenkinsRequestSettings,
        job_name: str,
) -> list or dict:
    """Obtains run information from job name"""
    return JsonUtils.get_json_response(f'{request_settings.url}/job/{job_name}/wfapi/runs',
                             request_settings.max_retry,
                             HttpRequestSettings(auth=request_settings.auth))
