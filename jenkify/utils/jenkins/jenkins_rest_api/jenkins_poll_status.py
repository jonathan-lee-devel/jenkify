"""Module containing code for polling Jenkins for specific status"""
import asyncio
import logging
import os
from http import HTTPStatus

from requests import Response
from typeguard import typechecked

from jenkify.constants.jenkins_env import JENKINS_USER, JENKINS_TOKEN
from jenkify.constants.jenkins_yaml import BUILD, HOSTS, JOBS, URL, END
from jenkify.enums.jenkins import JenkinsJobStatus
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings
from jenkify.utils.jenkins.jenkins_rest_api.jenkins_utils import JenkinsUtils
from jenkify.utils.logging_utils import logging_line_break


@typechecked
async def update_build_jobs_tracking_dict(
        build_jobs_statuses: list,
        build_jobs_tracking_dict: dict):
    """Updates build jobs tracking dictionary (usually outputted to YAML)"""
    for build_job_status in build_jobs_statuses:
        for host in build_jobs_tracking_dict[BUILD][HOSTS]:
            for job in host[JOBS]:
                if (build_job_status['host'] == host[URL] and
                        build_job_status[END] == job[END] and
                        build_job_status['build_number'] == job['build-index']):
                    job['status'] = build_job_status['status'].name


@typechecked
async def track_multiple_build_job_statuses(build_jobs_tracking_dict: dict):
    """Tracks multiple build job statuses"""
    url_combos: list[dict] = []
    for host_index in range(len(build_jobs_tracking_dict[BUILD][HOSTS])):
        host = build_jobs_tracking_dict[BUILD][HOSTS][host_index]
        for job_index in range(len(build_jobs_tracking_dict[BUILD][HOSTS][host_index][JOBS])):
            job = build_jobs_tracking_dict[BUILD][HOSTS][host_index][JOBS][job_index]
            url_combos.append({
                'host': host,
                'job': {'end': job['end'], 'build-index': job['build-index'],
                        'user-input': job.get('user-input', None)},
            })
    call_list = [poll_jenkins_job_for_desirable_status(
        JenkinsRequestSettings(url_combo['host'][URL],
                               (os.getenv(JENKINS_USER),
                                os.getenv(JENKINS_TOKEN)),
                               1),
        url_combo['job']['end'],
        url_combo['job']['build-index'],
        url_combo['job'].get('user-input', None)
    ) for url_combo in url_combos]
    statuses: list = list(await asyncio.gather(*call_list))
    await update_build_jobs_tracking_dict(statuses, build_jobs_tracking_dict)


@typechecked
async def poll_jenkins_job_for_desirable_status(jenkins_request_settings: JenkinsRequestSettings,
                                                url_end: str,
                                                build_number: int,
                                                user_input: list | None) -> dict:
    """Polls jenkins job continuously for success or unstable status"""
    jenkins_job_status: JenkinsJobStatus = JenkinsJobStatus.UNKNOWN
    none_responses_count = 0
    unknown_responses_count = 0
    should_poll = True
    while should_poll:
        response_dict = JenkinsUtils().get_jenkins_build_dict_url_end_build_number(
            url_end,
            build_number)
        if response_dict is None:
            none_responses_count += 1
            logging.debug('None response for %s #%s', url_end, build_number)
            if none_responses_count >= 10:
                logging.info('None response for %s #%s '
                             'None Response #%s',
                             url_end,
                             build_number,
                             none_responses_count)
                jenkins_job_status = JenkinsJobStatus.UNKNOWN
                logging.error(
                    'Result of %s #%s is None for the last '
                    '%s attempts, stopping polling!',
                    url_end,
                    build_number,
                    none_responses_count)
                break
            logging.info(
                'Continuing to poll %s #%s with status None'
                'response for attempt #%s',
                url_end,
                build_number,
                (none_responses_count + 1))
            await log_and_sleep(int(os.getenv('POLL_RATE_SECONDS')))
        elif response_dict['result'] == 'SUCCESS':
            handle_success_status(url_end, build_number)
            break
        elif response_dict['result'] == 'UNSTABLE':
            handle_unstable_status(url_end, build_number)
            break
        elif response_dict['result'] == 'UNKNOWN':
            unknown_responses_count += 1
            logging.info('UNKNOWN for %s #%s', url_end, build_number)
            if unknown_responses_count >= 10:
                handle_unknown_status_limit_reached(url_end, build_number, unknown_responses_count)
                break
            logging.info(
                'Continuing to poll %s #%s with status '
                'UNKNOWN for attempt #%s',
                url_end,
                build_number,
                (unknown_responses_count + 1))
            await log_and_sleep(int(os.getenv('POLL_RATE_SECONDS')))
        elif response_dict['result'] == 'FAILURE':
            logging.error('Result of %s #%s'
                          'is %s, stopping polling!',
                          url_end,
                          build_number,
                          JenkinsJobStatus.FAILURE)
            break
        elif response_dict['result'] == 'ABORTED':
            logging.error('Result of %s #%s'
                          'is %s, stopping polling!',
                          url_end,
                          build_number,
                          JenkinsJobStatus.ABORTED)
        else:
            await handle_pending_or_user_input_status(url_end, build_number, jenkins_request_settings, user_input)
            await log_and_sleep(int(os.getenv('POLL_RATE_SECONDS')))

    logging.info('Polling for %s #%s '
                 'complete with status %s!',
                 url_end,
                 build_number,
                 jenkins_job_status)
    logging_line_break()
    return {'host': jenkins_request_settings.url,
            END: url_end,
            'build_number': build_number,
            'status': jenkins_job_status}


async def log_and_sleep(seconds: int):
    logging.info('Sleeping for %s seconds...', seconds)
    await asyncio.sleep(seconds)
    logging_line_break()


@typechecked
def handle_success_status(url_end: str, build_number: int):
    logging.debug('Result of %s #%s is'
                  '%s, stopping polling!',
                  url_end,
                  build_number,
                  JenkinsJobStatus.SUCCESS)


@typechecked
def handle_unstable_status(url_end: str, build_number: int):
    logging.debug('Result of %s #%s is '
                  '%s, stopping polling!',
                  url_end,
                  build_number,
                  JenkinsJobStatus.UNSTABLE)


@typechecked
def handle_unknown_status_limit_reached(url_end: str, build_number: int, unknown_responses_count: int):
    logging.debug('UNKNOWN for %s #%s %s',
                  url_end,
                  build_number,
                  unknown_responses_count)
    jenkins_job_status = JenkinsJobStatus.UNKNOWN
    logging.error(
        'Result of %s #%s is %s'
        'for the last %s attempts, stopping polling!',
        url_end,
        build_number,
        jenkins_job_status,
        unknown_responses_count)


@typechecked
async def handle_pending_or_user_input_status(url_end: str, build_number: int,
                                              jenkins_request_settings: JenkinsRequestSettings,
                                              user_input: list | None = None):
    if (user_input_status := JenkinsUtils().query_jenkins_job_for_user_input(url_end, build_number)) is not None:
        if user_input is None:
            logging.info('Awaiting input for %s',
                         f'{jenkins_request_settings.url}/{url_end}/{build_number}/input')
        else:
            logging.info('Simulating input for %s',
                         f'{url_end} #{build_number}')
            input_simulation_response: Response = JenkinsUtils().simulate_jenkins_job_user_input(url_end,
                                                                                                 build_number,
                                                                                                 user_input_status[
                                                                                                     'id'],
                                                                                                 user_input)
            if input_simulation_response is not None and input_simulation_response.status_code == HTTPStatus.OK:
                logging.info('Input for %s simulated successfully!',
                             f'{jenkins_request_settings.url}/{url_end}/{build_number}/input')
    else:
        logging.info('Continuing to poll %s #%s with status: PENDING...',
                     url_end,
                     build_number)
