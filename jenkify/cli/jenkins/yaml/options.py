"""Jenkins YAML parsing command-line options"""
import click
from typeguard import typechecked


@typechecked
def build_jobs_yaml_file_option(func):
    """Build jobs YAML file"""
    return click.option('-bjy',
                        '--build-jobs-yaml',
                        type=click.STRING,
                        is_flag=False,
                        required=True,
                        help='Build jobs YAML file path'
                        )(func)


@typechecked
def build_jobs_tracking_yaml_file_option(func):
    """Build jobs tracking YAML file"""
    return click.option('-bjty',
                        '--build-jobs-tracking-yaml',
                        type=click.STRING,
                        is_flag=False,
                        required=True,
                        help='Build jobs tracking YAML file path'
                        )(func)
