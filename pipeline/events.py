from functools import wraps
import json

def invoke(f):

    @wraps(f)
    def wrapper(self, event, context):
        return f(self, event, context)
    wrapper.id = "lambda"
    return wrapper

def http(path, method, cors):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            data = json.loads(event['body'])
            return f(self, data, context)
        wrapped_f.id = 'http'
        wrapped_f.args = {'path': path, 'method': method, 'cors': cors}
        return wrapped_f
    return wrapper

def sns(resource):

    def wrapper(f):
        @wraps(f)
        def wrapped_f(self, event, context):
            data = json.loads(event['Records'][0]['Sns']['Message'])
            return f(self, data, context)
        wrapped_f.id = 'sns'
        wrapped_f.args = {'arn': resource.arn, 'topic_name': resource.name}
        return wrapped_f
    return wrapper

def sqs(resource):

    def wrapper(f):
        @wraps(f)
        def wraped_f(self, event, context):
            for record in event['Records']:
                data = json.loads(record['body'])
                output = f(self, data, context)
            return
        wraped_f.id = 'sqs'
        wraped_f.args = {'arn': resource.arn, 'url': resource.url, 'queue_name': resource.name}
        return wraped_f
    return wrapper