import yaml
import boto3

client = boto3.client("sts")


class Execution(object):

    """Object which defines the execution environment for the pipeline"""

    def __init__(self):
        self.__runtime = "python3.6"
        self.__region = "us-east-1"
        self.__stage = "dev"
        self.__accountid = client.get_caller_identity()["Account"]

    @property
    def runtime(self):
        return self.__runtime

    @runtime.setter
    def runtime(self, value):
        self.__runtime = value

    @property
    def region(self):
        return self.__region

    @region.setter
    def region(self, value):
        self.__region = value

    @property
    def stage(self):
        return self.__stage

    @stage.setter
    def stage(self, value):
        self.__stage = value

    @property
    def accountid(self):
        return self.__accountid


execution = Execution()
