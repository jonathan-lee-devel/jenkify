"""Commands to demonstrate CLI capabilities"""
import json
import logging
import os
import sys
from abc import ABC

import click
import yaml
from dotenv import load_dotenv
from typeguard import typechecked

from jenkify.cli.common.options import verbose_option
from jenkify.cli.jenkins.basic.options import job_name_option
from jenkify.cli.jenkins.example.options import with_failure_option
from jenkify.constants.jenkins_env import JENKINS_URL, JENKINS_USER, JENKINS_TOKEN
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings
from jenkify.utils.jenkins.jenkins_wfapi.base import get_job_name_and_run_count
from jenkify.utils.jenkins.jenkins_wfapi.runs import get_job_runs_response_content
from jenkify.utils.logging_utils import initialize_logging, logging_line_break


@click.group(name='jenkins_example_commands')
def jenkins_example_commands() -> None:
    """Entry point"""


class ExampleCommands(ABC):
    @jenkins_example_commands.command()
    @verbose_option
    @with_failure_option
    @staticmethod
    @typechecked
    def example_output(verbose: bool, with_failure: bool) -> None:
        """Displays example output for Jenkins multi-job run"""
        load_dotenv()
        initialize_logging(verbose)
        logging_line_break()
        logging.info('\n%s', yaml.dump(({
            'jobs': [
                {
                    'name': 'TestJob',
                    'build': 2,
                    'status': 'SUCCESS',
                    'url': 'http://localhost:8080/job/TestJob/2'
                }
            ]
        }) if not with_failure else {
            'jobs': [
                {
                    'name': 'TestJob',
                    'build': 2,
                    'status': 'FAILURE',
                    'url': 'http://localhost:8080/job/TestJob/2'
                }
            ]
        }))
        logging_line_break()
        if with_failure:
            sys.exit(1)

    @jenkins_example_commands.command()
    @verbose_option
    @job_name_option
    @staticmethod
    @typechecked
    def get_run_count(verbose: bool, job_name: str) -> None:
        """Gets the run count for a specific job"""
        load_dotenv()
        initialize_logging(verbose)
        logging_line_break()
        logging.info('%s', json.dumps(get_job_name_and_run_count(
            JenkinsRequestSettings(
                os.getenv(JENKINS_URL),
                (os.getenv(JENKINS_USER), os.getenv(JENKINS_TOKEN)),
                1,
            ),
            job_name,
        ), indent=2))

    @jenkins_example_commands.command()
    @verbose_option
    @job_name_option
    @staticmethod
    @typechecked
    def get_job_runs_content(verbose: bool, job_name: str) -> None:
        """Gets the run data for a specific job"""
        load_dotenv()
        initialize_logging(verbose)
        logging_line_break()
        logging.info('%s', json.dumps(get_job_runs_response_content(
            JenkinsRequestSettings(
                os.getenv(JENKINS_URL),
                (os.getenv(JENKINS_USER), os.getenv(JENKINS_TOKEN)),
                1,
            ),
            job_name,
        ), indent=2))
