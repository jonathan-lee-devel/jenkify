"""Jenkins commands which involve YAML parsing"""
import asyncio
import copy
import logging
import sys
from abc import ABC

import click
import yaml
from click import FileError
from dotenv import load_dotenv
from typeguard import typechecked

from jenkify.cli.common.options import verbose_option
from jenkify.cli.jenkins.yaml.options import (
    build_jobs_tracking_yaml_file_option,
    build_jobs_yaml_file_option,
)
from jenkify.constants.jenkins_yaml import BUILD, HOSTS, SUCCESSFUL_JOBS, FAILED_JOBS
from jenkify.use_cases.jenkins_build_job_tracking import validate_jenkins_job_build_tracking_yaml
from jenkify.use_cases.jenkins_builds import process_build_host
from jenkify.utils.jenkins.jenkins_rest_api.jenkins_poll_status import (
    track_multiple_build_job_statuses,
)
from jenkify.utils.logging_utils import initialize_logging, logging_line_break


@click.group(name='jenkins_yaml_commands')
def jenkins_yaml_commands() -> None:
    """Entry point"""


class YamlCommands(ABC):
    @jenkins_yaml_commands.command()
    @verbose_option
    @build_jobs_yaml_file_option
    @staticmethod
    @typechecked
    def start_build_jobs_yaml(verbose: bool, build_jobs_yaml: str) -> None:
        """Kicks off Jenkins jobs based on YAML input"""
        load_dotenv()
        initialize_logging(verbose)
        logging_line_break()
        logging.info('Parsing YAML: %s...', build_jobs_yaml)
        successful_jobs = []
        failed_jobs = []
        try:
            with open(build_jobs_yaml, 'r', encoding='utf-8') as yaml_file_contents:
                build_jobs_dict = yaml.safe_load(yaml_file_contents)
                for build_host_index, build_host in enumerate(build_jobs_dict[BUILD][HOSTS]):
                    jobs_info_dict: dict = process_build_host(build_host)
                    successful_jobs.append(jobs_info_dict[SUCCESSFUL_JOBS])
                    failed_jobs.append(jobs_info_dict[FAILED_JOBS])
        except FileError as exception:
            logging.fatal("Could not load file: %s -> %s", build_jobs_yaml, exception.message)
            sys.exit(1)

        logging.info('Run of %s completed:', build_jobs_yaml)
        logging.debug('Successful builds: %s', jobs_info_dict[SUCCESSFUL_JOBS])
        tracking_output_filename = build_jobs_yaml.replace('.yaml', '-tracking.yaml')
        logging.info('Writing build numbers to track to %s...', tracking_output_filename)
        tracking_build_jobs_dict = copy.deepcopy(build_jobs_dict)
        remaining_build_jobs_dict = copy.deepcopy(build_jobs_dict)
        for build_host in tracking_build_jobs_dict[BUILD][HOSTS]:
            build_host['jobs'] = list(filter(lambda job: job.get('build-index', -1) != -1, build_host['jobs']))

        try:
            with open(tracking_output_filename, 'w', encoding='utf-8') as output_file:
                yaml.dump(tracking_build_jobs_dict, output_file)
            if len(jobs_info_dict[FAILED_JOBS]) > 0:
                logging.debug('Failed builds: %s', jobs_info_dict[FAILED_JOBS])
                for build_host_index, build_host in enumerate(remaining_build_jobs_dict[BUILD][HOSTS]):
                    failed_jobs_dict = list(filter(lambda job: job.get('build-index', -1) == -1, build_host['jobs']))
                    remaining_build_jobs_dict[BUILD][HOSTS][build_host_index]['jobs'] = failed_jobs_dict
                output_file_name = build_jobs_yaml.replace('.yaml', '-remaining.yaml')
                logging.info('Outputting remaining (failed) jobs to %s...', output_file_name)
                with open(output_file_name, 'w', encoding='utf-8') as output_file:
                    yaml.dump(remaining_build_jobs_dict, output_file)
        except FileError as exception:
            logging.fatal("Could not load file: %s -> %s", build_jobs_yaml, exception.message)
            sys.exit(1)

        logging_line_break()


    @jenkins_yaml_commands.command()
    @verbose_option
    @build_jobs_tracking_yaml_file_option
    @staticmethod
    @typechecked
    def track_build_jobs_status(verbose: bool, build_jobs_tracking_yaml: str):
        """Tracks build job status"""
        load_dotenv()
        initialize_logging(verbose)
        logging.info('Validating tracking build jobs YAML: %s...', build_jobs_tracking_yaml)
        validation_errors = validate_jenkins_job_build_tracking_yaml(build_jobs_tracking_yaml)
        if len(validation_errors) > 0:
            logging.error(
                'Invalid build jobs tracking YAML: %s, Validation errors:',
                build_jobs_tracking_yaml)
            for validation_error in validation_errors:
                logging.error('Validation Failed for: field: %s -> %s',
                              validation_error.field,
                              validation_error.message)
            sys.exit(1)
        logging.info('Successfully validated tracking builds jobs YAML: %s!', build_jobs_tracking_yaml)
        try:
            with open(build_jobs_tracking_yaml, 'r', encoding='utf-8') as build_jobs_tracking_file:
                build_jobs_tracking_dict = yaml.safe_load(build_jobs_tracking_file)
                logging.info('Tracking builds asynchronously...')
                loop = asyncio.get_event_loop()
                loop.run_until_complete(track_multiple_build_job_statuses(build_jobs_tracking_dict))
                loop.close()
            with open(build_jobs_tracking_yaml, 'w', encoding='utf-8') as build_jobs_tracking_file:
                yaml.dump(build_jobs_tracking_dict, build_jobs_tracking_file)
        except FileError as exception:
            logging.fatal("Could not load file: %s -> %s", build_jobs_tracking_yaml, exception.message)
            sys.exit(1)

        logging.info('Wrote statuses to %s', build_jobs_tracking_yaml)
