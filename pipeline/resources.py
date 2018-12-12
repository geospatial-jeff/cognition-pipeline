import json
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
        return self['Type'].split('::')[1]


class SNSTopic(ServerlessResource):

    """Base class representing a SNS Topic.  Inherit and extend using dict interface."""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SNS::Topic'
        self['Properties'] = {'TopicName': self.name}

    def send_message(self, message):
        sns_client.publish(Message=json.dumps(message), TopicArn=self.arn)


class SQSQueue(ServerlessResource):

    """Base class representing a SQS Queue.  Inherit and extend using dict interface."""

    def __init__(self):
        super().__init__()
        self['Type'] = 'AWS::SQS::Queue'
        self['Properties'] = {'QueueName': self.name}

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

class ResourceGroup(object):

    """
    Object used to load resources into a pipeline.  Dynamically generates useful information like resource ARN.
    """

    @classmethod
    def load_resources(cls, *args, execution):
        """Class method to load specified resources into the group"""
        loaded = {}
        for item in args:
            res = item()
            if res['Type'] == 'AWS::SQS::Queue':
                arn = f"arn:aws:sqs:{execution.region}:{execution.accountid}:{res.name}"
                res.url = f"https://sqs-{execution.region}.amazonaws.com/{execution.accountid}/{res.name}"
            elif res['Type'] == 'AWS::SNS::Topic':
                arn = f"arn:aws:sns:{execution.region}:{execution.accountid}:{res.name}"
            else:
                raise InvalidResource("The resource is not recognized: {}".format(res.name))
            res.arn = arn
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