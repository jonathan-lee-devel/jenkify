"""Module containing code for polling Jenkins for specific status"""
import asyncio
import logging
import os

from typeguard import typechecked

from jenkify.constants.jenkins_env import JENKINS_USER, JENKINS_TOKEN
from jenkify.constants.jenkins_yaml import BUILD, HOSTS, JOBS, URL, END
from jenkify.enums.jenkins import JenkinsJobStatus
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings
from jenkify.utils.jenkins.jenkins_rest_api.jenkins_utils import JenkinsUtils


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
                'job': {'end': job['end'], 'build-index': job['build-index']}
            })
    call_list = [poll_jenkins_job_for_desirable_status(
        JenkinsRequestSettings(url_combo['host'][URL],
                               (os.getenv(JENKINS_USER),
                                os.getenv(JENKINS_TOKEN)),
                               1),
        url_combo['job']['end'],
        url_combo['job']['build-index']
    ) for url_combo in url_combos]
    statuses: list = list(await asyncio.gather(*call_list))
    await update_build_jobs_tracking_dict(statuses, build_jobs_tracking_dict)


@typechecked
async def poll_jenkins_job_for_desirable_status(jenkins_request_settings: JenkinsRequestSettings,
                                                url_end: str,
                                                build_number: int) -> dict:
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
            logging.debug('None response for %s #%s', url_end, build_number)
            none_responses_count += 1
            if none_responses_count >= 5:
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
            await asyncio.sleep(60)
        elif response_dict['result'] == 'SUCCESS':
            # pylint: disable=redefined-variable-type
            jenkins_job_status = JenkinsJobStatus.SUCCESS
            logging.debug('Result of %s #%s is'
                          '%s, stopping polling!',
                          url_end,
                          build_number,
                          jenkins_job_status)
            break
        elif response_dict['result'] == 'UNSTABLE':
            jenkins_job_status = JenkinsJobStatus.UNSTABLE
            logging.debug('Result of %s #%s is '
                          '%s, stopping polling!',
                          url_end,
                          build_number,
                          jenkins_job_status)
            break
        elif response_dict['result'] == 'UNKNOWN':
            logging.info('UNKNOWN for %s #%s', url_end, build_number)
            unknown_responses_count += 1
            if unknown_responses_count >= 5:
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
                break
            logging.info(
                'Continuing to poll %s #%s with status '
                'UNKNOWN for attempt #%s',
                url_end,
                build_number,
                (unknown_responses_count + 1))
            await asyncio.sleep(60)
        elif response_dict['result'] == 'FAILURE':
            jenkins_job_status = JenkinsJobStatus.FAILURE
            logging.error('Result of %s #%s'
                          'is %s, stopping polling!',
                          url_end,
                          build_number,
                          jenkins_job_status)
            break
        elif response_dict['result'] == 'ABORTED':
            jenkins_job_status = JenkinsJobStatus.ABORTED
            logging.error('Result of %s #%s'
                          'is %s, stopping polling!',
                          url_end,
                          build_number,
                          jenkins_job_status)
        else:
            logging.info('Continuing to poll %s #%s with status: PENDING...',
                         url_end,
                         build_number)
            await asyncio.sleep(60)
    logging.info('Polling for %s #%s '
                 'complete with status %s!',
                 url_end,
                 build_number,
                 jenkins_job_status)
    return {'host': jenkins_request_settings.url,
            END: url_end,
            'build_number': build_number,
            'status': jenkins_job_status}
