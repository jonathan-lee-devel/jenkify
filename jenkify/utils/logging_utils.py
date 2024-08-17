"""
Utilities file to store logging functions
"""
import logging

from typeguard import typechecked


@typechecked
def initialize_logging(verbose: bool = False):
    """
    Get the Root Logger and Set the Handlers and the Formatters
    :param verbose: Flag to set logging level to debug
    """
    logger = logging.getLogger('')
    if not logger.handlers:
        logger.setLevel(logging.DEBUG)
        console = logging.StreamHandler()
        formatter = logging.Formatter(
            '[%(levelname)s][%(filename)s:%(funcName)s:%(lineno)s][%(asctime)s] '
            '%(message)s')
        console.setFormatter(formatter)
        console.setLevel(logging.INFO)
        logger.addHandler(console)
    set_logging_verbosity_level(logger, verbose)


@typechecked
def set_logging_verbosity_level(logger: logging.Logger, verbose: bool):
    """
    Sets the verbosity level of the specified logger handler depending on the verbose
    option passed in
    :param logger: The logger to set the handler level for
    :param verbose: True or False
    """
    console = logger.handlers[0]
    if verbose:
        console.setLevel(logging.DEBUG)
    else:
        console.setLevel(logging.INFO)


def logging_line_break():
    """Logger formatting helper function which logs visual 'line-break'"""
    logging.info('============================================================')
