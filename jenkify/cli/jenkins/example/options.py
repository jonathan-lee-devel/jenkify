"""Example commands command-line options"""
import click
from typeguard import typechecked


@typechecked
def with_failure_option(func):
    """A decorator for the example output command"""
    return click.option('-wf', '--with-failure', type=click.BOOL, is_flag=True, required=False,
                        help='Include failure in example-output')(func)
