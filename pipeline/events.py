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
            if method == "get":
                data = event['pathParameters']
            else:
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
            record = event['Records'][0]
            if record['EventSource'] == 'aws:sns':
                data = record['Sns']['Message']
            elif record['EventSource'] == 'aws:s3':
                msg = json.loads(record['Sns']['message'])
                data = {'bucket': msg['s3']['bucket']['name'],
                        'key': msg['s3']['object']['key']}
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

def bucket_notification(bucket, event_type, destination, prefix=None):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            if destination.resource == 'sns':
                msg = json.loads(event['Records'][0]['Sns']['Message'])['Records'][0]
                data = {'bucket': msg['s3']['bucket']['name'],
                        'key': msg['s3']['object']['key']}
            elif destination.resource == 'sqs':
                for record in event['Records']:
                    body = json.loads(record['body'])
                    data = {'bucket': body['Records'][0]['s3']['bucket']['name'],
                            'key': body['Records'][0]['s3']['object']['key']
                            }
            return f(self, data, context)
        wrapped_f.trigger = 'bucket_notification'
        wrapped_f.args = {'bucket': bucket, 'event': event_type, 'destination': destination, 'prefix': prefix}
        return wrapped_f
    return wrapper


{"Records":[{"eventVersion":"2.1","eventSource":"aws:s3","awsRegion":"us-east-1","eventTime":"2019-01-04T17:40:07.181Z","eventName":"ObjectCreated:Put","userIdentity":{"principalId":"AWS:AIDAILOGY4ZN4UTP42ZTC"},"requestParameters":{"sourceIPAddress":"67.173.242.173"},"responseElements":{"x-amz-request-id":"C3481794F6CEFEDE","x-amz-id-2":"1nTYNl8Ogh1ncaK3c1o4qbKt4/8NrtdYOxb/u9PqEz1mNbB0zdOpm1xh9x11+N0qWCQBGXmSyDU="},"s3":{"s3SchemaVersion":"1.0","configurationId":"b9c99090-c658-4a0a-b79f-197e05c7c38a","bucket":{"name":"cognitionpipelinetests3","ownerIdentity":{"principalId":"AV5BH9QRC4DDJ"},"arn":"arn:aws:s3:::cognitionpipelinetests3"},"object":{"key":"sqs/notification.txt","size":14,"eTag":"ce114e4501d2f4e2dcea3e17b546f339","sequencer":"005C2F9A77119857B3"}}}]}
