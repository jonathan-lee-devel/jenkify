import unittest

from jenkify.utils.http_request_settings import HttpRequestSettings
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings
from jenkify.utils.jenkins.jenkins_rest_api.jenkins_utils import JenkinsUtils


def return_valid_json_response(
        _: str,
        __: int,
        ___: HttpRequestSettings
) -> dict | list:
    return {}


class MyTestCase(unittest.TestCase):

    def test_something(self):
        self.assertEqual(True, True)

    def test_get_jenkins_build_dict_when_invalid_max_retry_then_except(self):
        jenkins_utils = JenkinsUtils(jenkins_request_settings=JenkinsRequestSettings(
            max_retry=0,
            url='http://localhost:8080',
            auth=('user', 'token'),
        ))
        job_name: str = 'TestJob'
        build_number: int = 2
        with self.assertRaises(ValueError):
            jenkins_utils.get_jenkins_build_dict(job_name, build_number)


if __name__ == '__main__':
    unittest.main()
