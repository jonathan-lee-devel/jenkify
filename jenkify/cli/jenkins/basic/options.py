"""Jenkins CLI command options"""
import click
from typeguard import typechecked


@typechecked
def job_name_option(func):
    """Job name command line argument"""
    return click.option('-jn', '--job-name', type=click.STRING, is_flag=False, required=True,
                        help='Job name')(func)


@typechecked
def build_number_option(func):
    """Build number command line argument"""
    return click.option('-bn', '--build-number', type=click.INT, is_flag=False, required=True,
                        help='Build number')(func)


@typechecked
def url_end_option(func):
    """URL end command line argument"""
    return click.option('-ue', '--url-end', type=click.STRING, is_flag=False, required=True,
                        help='URL end')(func)
