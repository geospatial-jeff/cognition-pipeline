
import boto3

client = boto3.client('sts')

class Execution(object):

    def __init__(self):
        self.__runtime = 'python3.6'
        self.__region = 'us-east-1'
        self.__stage = 'dev'
        self.__accountid = client.get_caller_identity()['Account']

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

class Role(object):

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
        resources = [x for x in self.resource if x]
        actions = list(set(self.action))

        if len(actions) == 0 and len(resources) == 0:
            return

        policy = {
            "Effect": self.effect
        }
        if len(self.action) > 0:
            policy.update({"Action": actions})
        if len(self.resource) > 0:
            policy.update({"Resource": resources})
        return [policy]



execution = Execution()