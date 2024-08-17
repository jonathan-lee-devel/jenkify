"""Environment utilities abstract class module"""
import os
from abc import ABC

from dotenv import load_dotenv

from jenkify.constants.jenkins_env import JENKINS_URL, JENKINS_USER, JENKINS_TOKEN
from jenkify.utils.jenkins.jekins_request_settings import JenkinsRequestSettings


class Environment(ABC):
    @staticmethod
    def get_jenkins_request_settings_from_env() -> JenkinsRequestSettings:
        load_dotenv()
        return JenkinsRequestSettings(
            os.getenv(JENKINS_URL),
            (os.getenv(JENKINS_USER), os.getenv(JENKINS_TOKEN)),
            1,
        )
