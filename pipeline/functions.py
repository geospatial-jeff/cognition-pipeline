import os
import json
import re
from functools import wraps

import requests
import boto3

from .execution import execution
from .outputs import Outputs


class InvocationError(BaseException):
    pass


lambda_client = boto3.client('lambda')


class Function(object):
    """Object representing an AWS Lambda function and its trigger"""

    def __init__(self, func, pipeline_name):
        self.func = func
        self.name = self.func.__name__
        self.pipeline_name = pipeline_name
        self.trigger = func.trigger

    def template(self):
        raise NotImplementedError

    def package_function(self):
        """Package function with trigger"""
        func_info = {'handler': 'handler.' + self.name}
        trigger_info = self.template()
        if trigger_info:
            func_info.update(trigger_info)
        if hasattr(self.func, 'timeout'):
            func_info.update({'timeout': self.func.timeout})
        if hasattr(self.func, 'memory'):
            func_info.update({'memorySize': self.func.memory})
        return func_info


class Function_LAMBDA(Function):

    def __init__(self, func, pipeline_name):
        super().__init__(func, pipeline_name)

    def template(self):
        return None

    def invoke(self, data, invocation="RequestResponse"):
        long_name = f"{self.pipeline_name}-{execution.stage}-{self.name}"
        response = lambda_client.invoke(FunctionName=long_name,
                                        InvocationType=invocation,
                                        Payload=json.dumps(data))
        if invocation == "RequestResponse":
            response = json.loads(response['Payload'].read())
        return response


class Function_SNS(Function):

    def __init__(self, func, pipeline_name):
        super().__init__(func, pipeline_name)

    def template(self):
        return {
            "events": [
                {
                    "sns": {
                        "arn": self.func.args['arn'],
                        "topicName": self.func.args['topic_name']
                    }
                }
            ]
        }

    def invoke(self, data):
        from handler import pipeline
        resource = pipeline.resources[self.func.args['topic_name']]
        response = resource.send_message(data)


class Function_HTTP(Function):

    def __init__(self, func, pipeline_name):
        super().__init__(func, pipeline_name)

    def template(self):
        return {
            "events": [
                {
                    "http": {
                        "path": self.func.args['path'],
                        "method": self.func.args['method'],
                        "cors": self.func.args['cors']
                    }
                }
            ]
        }

    def invoke(self, data):
        outputs = Outputs.load('outputs.yml')
        full_path = os.path.join(outputs.endpoint(), self.func.args['path'])
        # there is am uch better way of doing this
        if '{' and '}' in full_path:
            regex = re.compile('{(.*?)\}')
            match = regex.findall(full_path)[0]
            full_path = full_path.replace("{" + match + "}", data)
        if self.func.args['method'] == 'get':
            r = requests.get(full_path)
        elif self.func.args['method'] == 'post':
            r = requests.post(full_path, data)
        if r.status_code == 200:
            response = r.content.decode('utf-8')
            return response
        else:
            raise InvocationError("Request returned with 404 code")


class Function_SQS(Function):

    def __init__(self, func, pipeline_name):
        super().__init__(func, pipeline_name)

    def template(self):
        return {
            "events": [
                {
                    "sqs": {
                        "arn": self.func.args['arn'],
                    }
                }
            ]
        }

    def invoke(self, data):
        from handler import pipeline
        resource = pipeline.resources[self.func.args['queue_name']]
        response = resource.send_message(data)
        return response


class Function_BUCKET_NOTIFICATION(Function):

    def __init__(self, func, pipeline_name):
        super().__init__(func, pipeline_name)

    def template(self):
        event_type = self.info['destination'].resource
        if event_type == 'sns':
            return {
                "events": [
                    {
                        "sns": {
                            "arn": self.info['destination'].arn,
                            "topicName": self.info['destination'].name
                        }
                    }
                ]
            }
        elif event_type == 'sqs':
            return {
                "events": [
                    {
                        "sqs": {
                            "arn": self.info['destination'].arn,
                        }
                    }
                ]
            }

    def invoke(self, data, **kwargs):
        from handler import pipeline
        resource = pipeline.resources[self.func.args['bucket'].name]
        if 'key' in kwargs.keys():
            key = kwargs['key']
        else:
            key = os.path.split(data)[-1]
        if data.endswith('.tif') or data.endswith('.jpg'):
            resource.upload_image(key, data)
        else:
            with open(data, 'r') as f:
                contents = f.read()
                resource.upload_file(key, contents)
        response = {'bucket': resource.name, 'key': key}
        return response

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