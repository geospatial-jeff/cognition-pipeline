import yaml
from .resources import ServerlessResource
from .execution import execution


class Role(object):

    """Object which defines IAM Role used by the pipeline and its lambda functions"""

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

        policy = {"Effect": self.effect}
        if len(self.action) > 0:
            policy.update({"Action": actions})
        if len(self.resource) > 0:
            policy.update({"Resource": resources})
        return [policy]


def include(fpath):
    class DummyResource(ServerlessResource):

        """Dummy resource class with build_resource method"""

        def __init__(self, name, template):
            ServerlessResource.__init__(self)
            self.update(template)
            self.name = name

        def build_resource(self):
            return self

        @property
        def arn(self):
            return f"arn:aws:{self.resource}:{execution.region}:{execution.accountid}:{self.name}"

    with open(fpath, "r") as stream:
        data = yaml.load(stream)
        res_list = [DummyResource(k, v) for (k, v) in data.items()]
        return res_list
