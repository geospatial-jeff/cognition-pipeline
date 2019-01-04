import boto3
import json
from functools import wraps

from . import triggers
from .execution import execution
from pipeline.outputs import Outputs

lambda_client = boto3.client('lambda')

class Function(object):

    """Object representing an AWS Lambda function and its trigger"""

    def __init__(self, func, pipeline_name):
        self.func = func
        self.pipeline_name = pipeline_name
        self.name = func.__name__
        self.trigger = getattr(triggers, func.trigger.upper())(func.args)


    def invoke(self, data, invocation="RequestResponse"):
        """Invoke the lambda function"""
        outputs = Outputs.load('outputs.yml')
        if self.trigger.name == 'lambda':
            long_name = f"{self.pipeline_name}-{execution.stage}-{self.name}"
            response = lambda_client.invoke(FunctionName=long_name,
                                            InvocationType=invocation,
                                            Payload=json.dumps(data))
            response = json.loads(response['Payload'].read())
        return response

    def package_function(self):
        """Package function with trigger"""
        func_info = {'handler': 'handler.'+self.name}
        trigger_info = self.trigger.template()
        if trigger_info:
            func_info.update(trigger_info)
        if hasattr(self.func, 'timeout'):
            func_info.update({'timeout': self.func.timeout})
        if hasattr(self.func, 'memory'):
            func_info.update({'memorySize': self.func.memory})
        return func_info

class FunctionGroup(object):

    """Object representing a group of functions.  Used internally to package lambda functions"""

    def __getitem__(self, item):
        return self.all[item]

    def __init__(self, functions):
        self.all = functions

    def to_dict(self):
        return {k:v.package_function() for (k,v) in self.all.items()}

def timeout(time):

    """Decorator to specify the lambda function's timeout"""

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            return f(self, event, context)
        wrapped_f.timeout = time
        return wrapped_f
    return wrapper


def memory(mem_mb):

    """
    Decorator to specify the lambda function's max memory size
    """

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            return f(self, event, context)
        wrapped_f.memory = mem_mb
        return wrapped_f
    return wrapper