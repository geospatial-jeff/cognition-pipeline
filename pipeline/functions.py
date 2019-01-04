import boto3
import json
import os
import re
from functools import wraps
import requests

from . import triggers
from .execution import execution
from pipeline.outputs import Outputs

lambda_client = boto3.client('lambda')

class InvocationError(BaseException):
    pass

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
            if invocation == "RequestResponse":
                response = json.loads(response['Payload'].read())
        elif self.trigger.name == 'http':
            endpoint = outputs.endpoint()
            path = self.trigger.template()['events'][0]['http']['path']
            method = self.trigger.template()['events'][0]['http']['method']
            full_path = os.path.join(endpoint, path)
            # there is a much better way of doing this
            if '{' and '}' in full_path:
                regex = re.compile('{(.*?)\}')
                match = regex.findall(full_path)[0]
                full_path = full_path.replace("{"+match+"}", data)
            if method == 'get':
                r = requests.get(full_path)
            elif method == 'post':
                r = requests.post(full_path, data)
            if r.status_code == 200:
                response = r.content.decode('utf-8')
            else:
                raise InvocationError("Request returned with 404 code")
        elif self.trigger.name == 'sns':
            import handler
            resource = getattr(handler, self.func.args['topic_name'])()
            response = resource.send_message(data)
        elif self.trigger.name == 'bucket_notification':
            import handler
            resource = getattr(handler, self.func.args['bucket'].name)()
            key = os.path.split(data)[-1]
            if data.endswith('.tif') or data.endswith('.jpg'):
                resource.upload_image(key, data)
            else:
                with open(data, 'r') as f:
                    contents = f.read()
                    resource.upload_file(key, contents)
            response = {'bucket': resource.name, 'key': key}
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