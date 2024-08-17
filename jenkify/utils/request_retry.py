"""
This module allows a user to attempt to make a request multiple times if the target host is
temporarily down
"""

import logging
import time
import requests
import urllib3
from typeguard import typechecked

from jenkify.enums.http_request_methods import HttpRequestMethod
from jenkify.exceptions.request_retry_exception import RequestRetryException
from jenkify.utils.http_request_settings import HttpRequestSettings

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


@typechecked
def request_retry_download_file(
        url: str,
        max_retry: int,
        request_settings: HttpRequestSettings,
        output_file_path: str) -> None:
    """
    Function which utilizes local request retry function to download file at specified URL
    :param url: of the file to download
    :param max_retry: Amount of times to retry the request
    :param request_settings: Settings for the request namely body, proxy, and SSL
    :param output_file_path: File path for the response body to be written to
    """
    response = request_retry(HttpRequestMethod.GET, url, max_retry, request_settings)
    logging.info('Writing response data to %s', output_file_path)
    with open(output_file_path, 'w', encoding='utf-8') as output_file:
        output_file.write(response.text)


@typechecked
def request_retry(
        request_method: HttpRequestMethod,
        url: str,
        max_retry: int,
        request_settings: HttpRequestSettings):
    """
    Function to retry requests if the target host is not found. Geometric retry is used here.
    :param request_method: Which REST request is being conducted
    :param url: URL you want to run your request against
    :param max_retry: Amount of times to retry the request
    :param request_settings: Settings for the request namely body, proxy, and SSL
    :return: response
    :rtype: requests.Response
    """
    count = 0
    response = None
    valid_response_codes = [
        requests.codes['ok'],
        requests.codes['created'],
        requests.codes['no_content']
    ]
    logging.debug('type_of_request: %s', request_method.name)
    logging.debug('url: %s', str(url))
    while count < max_retry:
        try:
            response = make_request_based_on_input(request_method, url, request_settings)
            if response and response.status_code in valid_response_codes:
                break
            logging.debug(
                'Raising RequestException as response status code is: %s',
                response.status_code)
            raise requests.exceptions.RequestException
        except requests.exceptions.RequestException:
            logging.debug('Could not make the %s request', request_method.name)
            logging.debug('Response status code: %s', str(response.status_code))
            logging.debug('Response reason: %s', str(response.reason))
            logging.debug('Response output: %s', str(response.text))

            if response.status_code == requests.codes['bad_request']:
                raise RequestRetryException('Bad request detected') \
                    from requests.exceptions.RequestException
        count += 1
        if count == max_retry:
            raise RequestRetryException(
                f'Failed to execute {request_method.name} request after {max_retry} tries'
            )

        sleep_time = 2 ** count
        logging.warning('Failed to make %s request. '
                        'Sleeping and then trying again in %s seconds',
                        request_method.name,
                        sleep_time)
        time.sleep(sleep_time)
    return response


@typechecked
def make_request_based_on_input(
        request_method: HttpRequestMethod,
        url: str,
        request_settings: HttpRequestSettings):
    """
    Makes a request based on the request type passed in
    :param request_method: Which REST request is being conducted
    :param url: URL you want to run your request against
    :param request_settings: Settings for the request namely body, proxy, and SSL
    :return: response
    :rtype: requests.Response
    """
    logging.debug('Trying to make %s request', request_method.name)
    response = None
    try:
        if request_method == HttpRequestMethod.GET:
            logging.debug('Doing a %s request', request_method.name)
            response = requests.get(url,
                                    proxies=request_settings.proxy,
                                    timeout=10,
                                    verify=request_settings.ssl,
                                    auth=request_settings.auth)
        elif request_method == HttpRequestMethod.PATCH:
            logging.debug('Doing a %s request', request_method.name)
            response = requests.patch(url,
                                      json=request_settings.body,
                                      timeout=20,
                                      proxies=request_settings.proxy,
                                      verify=request_settings.ssl,
                                      auth=request_settings.auth)
        elif request_method == HttpRequestMethod.PUT:
            logging.debug('Doing a %s request', request_method.name)
            response = requests.put(url,
                                    json=request_settings.body,
                                    timeout=5,
                                    proxies=request_settings.proxy,
                                    verify=request_settings.ssl,
                                    auth=request_settings.auth)
        elif request_method == HttpRequestMethod.POST:
            logging.debug('Doing a %s request', request_method.name)
            response = requests.post(url,
                                     json=request_settings.body,
                                     timeout=20,
                                     proxies=request_settings.proxy,
                                     verify=request_settings.ssl,
                                     auth=request_settings.auth)
        elif request_method == HttpRequestMethod.DELETE:
            logging.debug('Doing a %s request', request_method.name)
            response = requests.delete(url,
                                       timeout=10,
                                       proxies=request_settings.proxy,
                                       verify=request_settings.ssl)
    except (requests.exceptions.ProxyError, AssertionError):
        logging.error('Could not make %s request due to a Proxy Error', request_method.name)
    return response
