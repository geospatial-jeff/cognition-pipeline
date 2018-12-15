import inspect
import yaml

from . import resources, functions
from .utils import execution, Role

class Pipeline(object):

    def __init__(self, name, resource=None):
        self.name = name
        self.execution = execution
        if resource:
            self.resources = resources.ResourceGroup.load_resources(resource)
        else:
            self.resources = resource
        self.functions = functions.FunctionGroup.load_functions(self.lambdas(), self)
        self.role = Role(self.name)

    def lambdas(self):
        base_methods = [x[0] for x in inspect.getmembers(Pipeline, predicate=inspect.isfunction)]
        methods = [x[0] for x in inspect.getmembers(self, predicate=inspect.ismethod) if x[0] not in base_methods]
        return methods

    def define_role(self):
        if self.resources:
            for (k,v) in self.resources.all.items():
                self.role.add_resource(v.arn)
                self.role.add_action(v.resource.lower() + ':*')
        return self.role.to_dict()

    def deploy(self):

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
            "functions": self.functions.to_dict(), #Functions go here
            "plugins": ["serverless-python-requirements"]
        }

        if self.resources:
            sls_dict.update({"resources": self.resources.to_dict()})

        with open('serverless.yml', 'w') as outfile:
            yaml.dump(sls_dict, outfile, default_flow_style=False)