import json
from string import Formatter, Template
import boto3


sns_client = boto3.client('sns')
sqs_client = boto3.client('sqs')


class InvalidResource(BaseException):
    pass

class ServerlessResource(dict):

    """
    Base class representing a serverless resource, defining a specific type of AWS resource (SQS Queue, SNS Topic etc.).
    Serverless resources store data in two locations.  The object's inherited dict interface is used to define the
    underlying AWS cloudformation template while the object's attributes are used to store resource-specific information
    not required by cloudformation but useful when building and executing pipelines (ARN, SQS queue url, etc.)
    """

    def __init__(self):
        super().__init__()
        self.name = self.__class__.__name__
        self.__arn = None

    def build_resource(self):
        """Convert resource to dictionary structure compatible with SLS framework"""
        return {self.name: dict(self)}

    @property
    def arn(self):
        return self.__arn

    @arn.setter
    def arn(self, value):
        self.__arn = value

    @property
    def resource(self):
        return self['Type'].split('::')[1].lower()


class SNSTopic(ServerlessResource):

    """Base class representing a SNS Topic.  Inherit and extend using dict interface."""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SNS::Topic'
        self['Properties'] = {'TopicName': self.name}
        self.arn_pattern = 'arn:aws:sns:${region}:${accountid}:${name}'

    def send_message(self, message):
        sns_client.publish(Message=json.dumps(message), TopicArn=self.arn)

    def attach_policy(self, policy):
        policy['Properties']['PolicyDocument']['Id'] = self.name + '-policy'
        policy['Properties']['PolicyDocument']['Statement'][0]['Resource'] = self.arn
        policy['Properties']['Topics'].append(self.arn)
        policy.update({"DependsOn": [self.name]})
        return policy

class SNSPolicy(ServerlessResource):

    """Base class representing a SNS Topic Policy.  Inherit and extend using dict itnerface"""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SNS::TopicPolicy'
        self['Properties'] = {
                            "PolicyDocument": {
                                "Id": None,
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Principal": {
                                            "AWS": "*"
                                        },
                                        "Action": "sns:Publish",
                                        "Resource": None
                                    }
                                ]
                            },
                            "Topics": []
                        }

class SQSQueue(ServerlessResource):

    """Base class representing a SQS Queue.  Inherit and extend using dict interface."""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SQS::Queue'
        self['Properties'] = {'QueueName': self.name}

        self.arn_pattern = 'arn:aws:sqs:${region}:${accountid}:${name}'
        self.__url = None

    @property
    def url(self):
        return self.__url

    @url.setter
    def url(self, value):
        self.__url = value

    def send_message(self, message):
        sqs_client.send_message(QueueUrl=self.url,
                                MessageBody=json.dumps(message))

    def attach_policy(self, policy):
        policy['Properties']['PolicyDocument']['Id'] = self.name + '-policy'
        policy['Properties']['PolicyDocument']['Statement'][0]['Resource'] = self.arn
        policy['Properties']['Queues'].append(self.url)
        policy.update({"DependsOn": [self.name]})
        return policy


class SQSPolicy(ServerlessResource):

    """Base class representing a SQS Queue Policy.  Inherit and extend using dict itnerface"""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SQS::QueuePolicy'
        self['Properties'] = {
                            "PolicyDocument": {
                                "Id": None,
                                "Statement": [
                                    {
                                        "Effect": "Allow",
                                        "Principal": {
                                            "AWS": "*"
                                        },
                                        "Action": "sqs:*",
                                        "Resource": None
                                    }
                                ]
                            },
                            "Queues": []
                        }


class S3Bucket(ServerlessResource):

    """Base class representing an S3 Bucket.  Inherit and extend using dict interface"""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::S3::Bucket'
        self['Properties'] = {'BucketName': self.name.lower()}

        self.arn_pattern = 'arn:aws:s3:::${name}'

class ResourceGroup(object):

    """
    Object used to load resources into a pipeline.  Dynamically generates useful information like resource ARN.
    """
    @staticmethod
    def substitute_arn(res, execution):
        """https://github.com/sat-utils/sat-stac/blob/master/satstac/item.py"""
        string = res.arn_pattern
        subs = {}
        for key in [x[1] for x in Formatter().parse(string) if x[1] is not None]:
            if key == "region":
                subs[key] = execution.region
            elif key == "accountid":
                subs[key] = execution.accountid
            elif key == "name":
                subs[key] = res.name
        return Template(string).substitute(**subs)

    @classmethod
    def load_resources(cls, *args, execution):
        """Class method to load specified resources into the group"""
        loaded = {}
        for item in args:
            res = item()
            res.arn = cls.substitute_arn(res, execution)
            if res['Type'] == 'AWS::SQS::Queue':
                res.url = f"https://sqs-{execution.region}.amazonaws.com/{execution.accountid}/{res.name}"
            loaded.update({res.name: res})
        return cls(loaded)

    def __getitem__(self, item):
        return self.all[item]

    def __init__(self, resources):
        self.all = resources

    def update_resource(self, resource, new_resource):
        self.all[resource] = new_resource

    def add_resource(self, resource):
        self.all.update({resource.name: resource})

    def to_dict(self):
        """Dump all resources to dict"""
        resources = {"Resources": {}}
        dicts = [self.all[k].build_resource() for k in self.all.keys()]
        [resources['Resources'].update(_) for _ in dicts]
        return resources