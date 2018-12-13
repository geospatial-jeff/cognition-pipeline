import boto3

client = boto3.client('sts')

class Role(object):

    """IAM Role"""

    def __init__(self, name):
        self.name = name + "-role"
        self.effect = "Allow"
        self.action = []
        self.resource = []

    def add_action(self, value):
        self.action.append(value)

    def add_resource(self, value):
        self.resource.append(value)

    def to_dict(self):

        resource = [x for x in self.resource if x]

        if len(self.action) == 0 and len(resource) == 0:
            return

        policy = {
            "Effect": "Allow",
        }
        if len(self.action) > 0:
            policy.update({"Action": self.action})
        if len(self.resource) > 0:
            policy.update({"Resource": resource})
        return [policy]


class Execution(dict):

    def __init__(self):
        super().__init__()
        self.runtime = 'python3.6'
        self.region = 'us-east-1'
        self.stage = 'dev'
        self.accountid = client.get_caller_identity()['Account']

