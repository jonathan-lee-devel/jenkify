"""wfapi base endpoint utilities module"""
from typeguard import typechecked

from jenkify.utils.http_request_settings import HttpRequestSettings
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings
from jenkify.utils.json.JsonUtils import JsonUtils


@typechecked
def get_job_name_and_run_count(
        request_settings: JenkinsRequestSettings,
        job_name: str,
) -> dict:
    """Obtains job name and run count from job name"""
    response: dict = JsonUtils.get_json_response(f'{request_settings.url}/job/{job_name}/wfapi/',
                                       request_settings.max_retry,
                                       HttpRequestSettings(auth=request_settings.auth))
    return {'name': job_name, 'runCount': response['runCount']}
