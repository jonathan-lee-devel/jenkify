"""Jenkins REST API CLI commands module"""
import logging
from abc import ABC
from http import HTTPStatus

import click
from typeguard import typechecked

from jenkify.cli.common.options import verbose_option
from jenkify.cli.jenkins.basic.options import (
    job_name_option, build_number_option, url_end_option,
)
from jenkify.use_cases.jenkins_job_info import JenkinsJobInfoUseCase
from jenkify.utils.jenkins.jenkins_rest_api.jenkins_utils import JenkinsUtils
from jenkify.utils.logging_utils import initialize_logging


@click.group(name='jenkins_basic_commands')
def jenkins_basic_commands() -> None:
    """Entry point"""


class BasicCommands(ABC):
    @jenkins_basic_commands.command()
    @verbose_option
    @job_name_option
    @staticmethod
    @typechecked
    def start_build(verbose: bool, job_name: str) -> None:
        """Kicks off a Jenkins job build based on job name"""
        initialize_logging(verbose)
        logging.info('Kicking off build (%s)...', job_name)
        if JenkinsUtils().start_jenkins_build(job_name).status_code == HTTPStatus.CREATED:
            logging.info('Successfully kicked off build (%s)!', job_name)
        else:
            logging.error('Failed to kick off build (%s)!', job_name)

    @jenkins_basic_commands.command()
    @verbose_option
    @url_end_option
    @staticmethod
    @typechecked
    def start_build_url(verbose: bool, url_end: str) -> None:
        """Starts Jenkins job based on URL ending"""
        initialize_logging(verbose)
        logging.info('Kicking off build (%s)...', url_end)
        if (JenkinsUtils().start_jenkins_build_url_end(
                JenkinsUtils.trim_url_end_option_util(url_end)
        ) == HTTPStatus.CREATED):
            logging.info('Successfully kicked off build (%s)!', url_end)
        else:
            logging.error('Failed to kick off build (%s)!', url_end)

    @jenkins_basic_commands.command()
    @verbose_option
    @job_name_option
    @build_number_option
    @staticmethod
    @typechecked
    def get_console_output(verbose: bool, job_name: str, build_number: int) -> None:
        """Gets console output for specific Jenkins job build"""
        initialize_logging(verbose)
        logging.info('Getting console output for (%s) build number #%s...',
                     job_name,
                     build_number)
        logging.info('Console output: \n%s',
                     JenkinsUtils()
                     .get_jenkins_build_console_output(job_name, build_number))

    @jenkins_basic_commands.command()
    @verbose_option
    @job_name_option
    @build_number_option
    @staticmethod
    @typechecked
    def get_jenkins_build_json(verbose: bool, job_name: str, build_number: int) -> None:
        """Gets Jenkins job build JSON data from REST API"""
        initialize_logging(verbose)
        logging.info('Getting API JSON for (%s) build number #%s...',
                     job_name,
                     build_number)
        logging.info('Jenkins JSON: \n%s',
                     JenkinsUtils()
                     .get_jenkins_build_dict(job_name, build_number))

    @jenkins_basic_commands.command()
    @verbose_option
    @url_end_option
    @build_number_option
    @staticmethod
    @typechecked
    def get_jenkins_job_status(verbose: bool, url_end: str, build_number: int) -> None:
        """Gets jenkins_responses job status"""
        initialize_logging(verbose)
        url_end = JenkinsUtils.trim_url_end_option_util(url_end)
        logging.info('Getting job status for (%s) build number #%s...', url_end, build_number)
        job_status = JenkinsJobInfoUseCase().get_jenkins_job_result_status(url_end, build_number)
        logging.info('Jenkins job (%s) build number #%s status: %s',
                     url_end,
                     build_number,
                     job_status)
