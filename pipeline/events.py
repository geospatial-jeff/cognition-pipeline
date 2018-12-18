from functools import wraps
import json

"""
Decorators used to specify event type for lambda invocations. Uses functools.wraps to preserve the original function 
metadata, allowing this metadata to be accessable to the Pipeline object while outside the function's scope.  Each
decorator creates a `trigger` and `args` attribute on the decorated function which are used internally to orchestrate
configuration and deployment.
"""


def invoke(f):

    @wraps(f)
    def wrapper(self, event, context):
        return f(self, event, context)
    wrapper.trigger = "lambda"
    wrapper.args = {}
    return wrapper

def http(path, method, cors):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            data = json.loads(event['body'])
            return f(self, data, context)
        wrapped_f.trigger = 'http'
        wrapped_f.args = {'path': path, 'method': method, 'cors': cors}
        return wrapped_f
    return wrapper

def sns(resource):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            msg = json.loads(event['Records'][0]['Sns']['Message'])['Records'][0]
            if msg['eventSource'] == 'aws:s3':
                data = {'bucket': msg['s3']['bucket']['name'],
                        'key': msg['s3']['object']['key']}
            else:
                data = msg
            return f(self, data, context)
        wrapped_f.trigger = 'sns'
        wrapped_f.args = {'arn': resource.arn, 'topic_name': resource.name, 'func_name': f.__name__}
        return wrapped_f
    return wrapper

def sqs(resource):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            for record in event['Records']:
                data = json.loads(record['body'])
                output = f(self, data, context)
            return
        wrapped_f.trigger = 'sqs'
        wrapped_f.args = {'arn': resource.arn, 'url': resource.url, 'queue_name': resource.name}
        return wrapped_f
    return wrapper

def bucket_notification(bucket, event_type, destination):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            if destination.resource == 'sns':
                msg = json.loads(event['Records'][0]['Sns']['Message'])['Records'][0]
                data = {'bucket': msg['s3']['bucket']['name'],
                        'key': msg['s3']['object']['key']}
            return f(self, data, context)
        wrapped_f.trigger = 'bucket_notification'
        wrapped_f.args = {'bucket': bucket, 'event': event_type, 'destination': destination}
        return wrapped_f
    return wrapper