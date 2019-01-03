import inspect
import yaml

from .utils import Role
from .execution import execution
from . import triggers, functions
from . import resources as res

class Pipeline(object):

    """
    Base class representing an AWS Pipeline which may be inherited to build a custom pipeline:

        - Methods represent lambda functions
        - Decorators change the invocation trigger of the lambda function
        - Resources may be constructed using the appropriate base class and passed into the pipeline
        - Services may be imported into the pipeline
    """

    def __init__(self, name, resources=None, services=None):
        self.name = name
        self.execution = execution
        self.functions = self.load_functions()
        if resources:
            self.resources = res.ResourceGroup.load_resources(resources)
        else:
            self.resources = resources
        self.role = Role(self.name)
        self.services = services

    def lambdas(self):
        """Return names of pipeline's methods (lambda functions)"""
        base_methods = [x[0] for x in inspect.getmembers(Pipeline, predicate=inspect.isfunction)]
        methods = [x[0] for x in inspect.getmembers(self, predicate=inspect.ismethod) if x[0] not in base_methods]
        lambdas = [x for x in methods if 'trigger' in dir(getattr(self,x))]
        return lambdas

    def load_functions(self):
        """Load functions into a FunctionGroup"""
        return functions.FunctionGroup({fname:functions.Function(getattr(self, fname)) for fname in self.lambdas()})

    def define_role(self):
        """Define the pipeline's IAM role based on available resources"""
        if self.resources:
            for (k,v) in self.resources.all.items():
                if 'policy' not in v['Type'].lower():
                    if 's3' in v['Type'].lower():
                        self.role.add_resource('arn:aws:s3:::*')
                    else:
                        self.role.add_resource(v.arn)
                    self.role.add_action(v.resource.lower() + ':*')
        return self.role.to_dict()

    def deploy(self):
        """Generate a serverless.yml file of the pipeline which may be deployed with Serverless Framework"""
        # Bucket notifications require setting up some additional policies.  Do this outside scope of lambda execution
        # so we aren't creating resource templates during runtime.
        # A lot of this could be abstracted to the resource object itself
        for (k,v) in self.functions.all.items():
            if v.trigger.name == 'bucket_notification':
                bucket = v.trigger.info['bucket'] #Bucket resource
                destination = v.trigger.info['destination'] #Destination resource
                event = v.trigger.info['event']
                if destination.resource == 'sns':
                    # Bucket configuration
                    topic_configuration = [
                        {
                            "Topic": destination.arn,
                            "Event": event,
                        }
                    ]
                    bucket['Properties'].update(
                        {'NotificationConfiguration': {'TopicConfigurations': topic_configuration}})
                    # SNS Policy
                    policy = res.SNSPolicy()
                    destination.attach_policy(policy)
                elif destination.resource == 'sqs':
                    # Bucket configuration
                    queue_configuration = [
                        {
                            "Queue": destination.arn,
                            "Event": event,
                        }
                    ]
                    bucket['Properties'].update(
                        {'NotificationConfiguration': {'QueueConfigurations': queue_configuration}})
                    # SQS Policy
                    policy = res.SQSPolicy()
                    destination.attach_policy(policy)
                bucket.update({"DependsOn": [policy.name]})
                self.resources.update_resource(bucket.name, bucket)
                self.resources.add_resource(policy)

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
            "functions": self.functions.to_dict(),
            "plugins": ["serverless-python-requirements"]
        }

        if self.resources:
            sls_dict.update({"resources": self.resources.to_dict()})

        with open('serverless.yml', 'w') as outfile:
            yaml.dump(sls_dict, outfile, default_flow_style=False)

        if self.services:
            with open('requirements.txt', 'a+') as reqfile:
                for service in self.services:
                    for req in service.requirements():
                        reqfile.write(req + "\n")