import boto3
import json

from .utils import execution

s3_res = boto3.resource('s3')
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
        """Return resource type (sns, sqs etc.)"""
        return self['Type'].split('::')[1].lower()

class SNSTopic(ServerlessResource):

    """Base class representing a SNS Topic.  Inherit and extend using dict interface"""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SNS::Topic'
        self['Properties'] = {'TopicName': self.name}

    @property
    def arn(self):
        return f"arn:aws:sns:{execution.region}:{execution.accountid}:{self.name}"

    def attach_policy(self, policy):
        policy['Properties']['PolicyDocument']['Id'] = self.name + '-policy'
        policy['Properties']['PolicyDocument']['Statement'][0]['Resource'] = self.arn
        policy['Properties']['Topics'].append(self.arn)
        policy.update({"DependsOn": [self.name]})
        return policy

class SNSPolicy(ServerlessResource):

    """Base class representing a SNS Topic Policy.  Inherit and extend using dict interface"""

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
    def arn(self):
        return f"arn:aws:sqs:{execution.region}:{execution.accountid}:{self.name}"

    @property
    def url(self):
        return f"https://sqs-{execution.region}.amazonaws.com/{execution.accountid}/{self.name}"

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

    @property
    def arn(self):
        return f'arn:aws:s3:::{self.name}'

    def upload_file(self, key, data):
        object = s3_res.Object(self.name.lower(), key)
        object.put(Body=data)

    def upload_image(self, key, file):
        s3_res.Bucket(self.name.lower()).upload_file(file, key)

    def read_file(self, key):
        object = s3_res.Object(self.name.lower(), key)
        file_content = object.get()['Body'].read().decode('utf-8')
        return file_content

    def download_image(self, key, file):
        s3_res.Bucket(self.name.lower()).download_file(key, file)

class ResourceGroup(object):

    """Object representing a group of resources.  Used internally to package resources"""

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

    def update_resource(self, resource, new_resource):
        self.all[resource] = new_resource

    def add_resource(self, resource):
        self.all.update({resource.name: resource})