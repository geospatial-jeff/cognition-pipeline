import boto3
import json

from .utils import execution

sqs_client = boto3.client('sqs')

class ServerlessResource(dict):

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__

    def build_resource(self):
        """Convert resource to dictionary structure compatible with SLS framework"""
        return {self.name: dict(self)}

    @property
    def resource(self):
        return self['Type'].split('::')[1].lower()

class SNSTopic(ServerlessResource):

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SNS::Topic'
        self['Properties'] = {'TopicName': self.name}

    @property
    def arn(self):
        return f"arn:aws:sns:{execution.region}:{execution.accountid}:{self.name}"

class SQSQueue(ServerlessResource):

    """Base class representing a SQS Queue.  Inherit and extend using dict interface."""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SQS::Queue'
        self['Properties'] = {'QueueName': self.name}

        self.arn_pattern = 'arn:aws:sqs:${region}:${accountid}:${name}'
        self.__url = None

    @property
    def arn(self):
        return f"arn:aws:sns:{execution.region}:{execution.accountid}:{self.name}"

    @property
    def url(self):
        return f"https://sqs-{execution.region}.amazonaws.com/{execution.accountid}/{self.name}"

    def send_message(self, message):
        sqs_client.send_message(QueueUrl=self.url,
                                MessageBody=json.dumps(message))

class ResourceGroup(object):

    @classmethod
    def load_resources(cls, res_list):
        loaded = {}
        for item in res_list:
            res = item()
            loaded.update({res.name: res})
        return cls(loaded)

    def __getitem__(self, item):
        return self.all[item]

    def __init__(self, resources):
        self.all = resources

    def to_dict(self):
        """Dump all resources to dict"""
        resources = {"Resources": {}}
        dicts = [self.all[k].build_resource() for k in self.all.keys()]
        [resources['Resources'].update(_) for _ in dicts]
        return resources
