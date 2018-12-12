import inspect
import yaml
import boto3

from . import utils, resources

client = boto3.client('sts')


class DeployError(BaseException):
    pass

class Pipeline(object):

    def __init__(self, name, resource=None, services=None):
        self.name = name
        self.execution = utils.Execution()
        self.services = services
        self.resources = resources.ResourceGroup.load_resources(*resource, execution=self.execution)
        self.role = utils.Role(self.name)
        self.mode = "deployed"

    def functions(self):
        base_methods = [x[0] for x in inspect.getmembers(Pipeline, predicate=inspect.isfunction)]
        methods = [x[0] for x in inspect.getmembers(self, predicate=inspect.ismethod)]
        func_names = list(set(methods)-set(base_methods))
        func_info = {}
        [func_info.update(getattr(self, x)(None, None)) for x in func_names]
        return func_info

    def define_role(self):
        for (k,v) in self.resources.all.items():
            self.role.add_resource(v.arn)
            self.role.add_action(v.resource.lower() + ':*')
        return self.role.to_dict()

    def deploy(self):
        self.mode = "deploy"
        functions = self.functions()

        if not self.name:
            raise DeployError("Specify name in pipeline (self.name = <pipeline name>)")

        sls_dict = {
            "service": self.name,
            "provider": {
                "name": "aws",
                "runtime": self.execution.runtime,
                "region": self.execution.region,
                "stage": self.execution.stage,
                "iamRoleStatementsName": self.role.name,
                "iamRoleStatements": self.define_role()
            },
            "functions": functions, #Functions go here
            "resources": self.resources.to_dict()
        }

        with open('serverless.yml', 'w') as outfile:
            yaml.dump(sls_dict, outfile, default_flow_style=False)

        with open('requirements.txt', 'w') as reqfile:
            for service in self.services:
                for req in service.requirements():
                    reqfile.write(req + "\n")