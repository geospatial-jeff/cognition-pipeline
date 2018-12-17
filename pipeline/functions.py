import boto3
import json
from functools import wraps
from . import triggers

lambda_client = boto3.client('lambda')

class Function(object):

    def __init__(self, func):
        self.func = func
        self.name = func.__name__
        self.trigger = getattr(triggers, func.trigger.upper())(func.args)


    def invoke(self, data, invocation="Event"):
        response = lambda_client.invoke(FunctionName=self.name,
                                        InvocationType=invocation,
                                        Payload=json.dumps(data))
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

    def __getitem__(self, item):
        return self.all[item]

    def __init__(self, functions):
        self.all = functions

    def to_dict(self):
        return {k:v.package_function() for (k,v) in self.all.items()}

def timeout(time):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            return f(self, event, context)
        wrapped_f.timeout = time
        return wrapped_f
    return wrapper


def memory(mem_mb):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            return f(self, event, context)
        wrapped_f.memory = mem_mb
        return wrapped_f
    return wrapper