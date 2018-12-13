import json
from string import Formatter
from . import resources

def invoke(f):

    def wrapper(self, event, context):
        if self.mode == "deploy":
            func_info = {
                "handler": f"handler.{f.__name__}"
            }
            return {f.__name__: func_info}
        return f(self, event, context)
    return wrapper

def http(path, method, cors):

    def wrap(f):
        def wrapped_f(self, event, context):
            if self.mode == "deploy":
                func_info = {
                    "handler": f"handler.{f.__name__}",
                    "events": [
                        {
                            "http": {
                                "path": path,
                                "method": method,
                                "cors": cors,
                            }
                        }
                    ]
                }
                return {f.__name__: func_info}
            data = json.loads(event['body'])
            return f(self, data, context)
        return wrapped_f
    return wrap

def sns(resource):

    def wrap(f):
        def wrapped_f(self, event, context):
            if self.mode == "deploy":
                topicname = resource().name
                arn = self.resources[topicname].arn
                func_info = {
                    "handler": f"handler.{f.__name__}",
                    "events": [
                        {
                            "sns": {
                                "arn": arn,
                                "topicName": topicname
                            }
                        }
                    ]
                }
                return {f.__name__: func_info}
            #Load sns message
            data = json.loads(event['Records'][0]['Sns']['Message'])
            return f(self, data, context)
        return wrapped_f
    return wrap

def sqs(resource):

    def wrap(f):
        def wrapped_f(self, event, context):
            if self.mode == "deploy":
                topicname = resource().name
                arn = self.resources[topicname].arn
                func_info = {
                    "handler": f"handler.{f.__name__}",
                    "events": [
                        {
                            "sqs": {
                                "arn": arn,
                            }
                        }
                    ]
                }
                return {f.__name__: func_info}
            #Load sns message
            data = json.loads(event['Records'][0]['Sns']['Message'])
            return f(self, data, context)
        return wrapped_f
    return wrap

def bucket_notification(bucket, event_type, destination):

    """Bucket supports lambda, queue, and topic configurations"""

    def wrap(f):
        def wrapped_f(self, event, context):
            dest = self.resources[destination().name]
            if self.mode == "deploy":
                bucket_mod = bucket()
                destination_name = dest.name
                destination_arn = dest.arn
                #Add a notification configuration based on destination type
                if dest.resource == "sqs":
                    # Bucket configuration
                    queue_configuration = [
                        {
                            "Queue": destination_arn,
                            "Event": event_type,
                        }
                    ]
                    bucket_mod['Properties'].update({'NotificationConfiguration': {'QueueConfigurations': queue_configuration}})
                    # SQS Policy
                    policy = resources.SQSPolicy()
                    policy = dest.attach_policy(policy)
                elif dest.resource == "sns":
                    topic_configuration = [
                        {
                            "Topic": destination_arn,
                            "Event": event_type,
                        }
                    ]
                    bucket_mod['Properties'].update({'NotificationConfiguration': {'TopicConfigurations': topic_configuration}})
                    # SNS Policy
                    policy = resources.SNSPolicy()
                    policy = dest.attach_policy(policy)
                # Update resource to include notification configuration
                bucket_mod.update({"DependsOn": [policy.name]})
                self.resources.update_resource(bucket_mod.name, bucket_mod)
                # Add policy
                self.resources.add_resource(policy)

                # Return function handler
                func_info = {
                    "handler": f"handler.{f.__name__}",
                    "events": [
                        {
                            dest.resource: {
                                "arn": destination_arn,
                                "topicName": destination_name
                            }
                        }
                    ]
                }
                return {f.__name__: func_info}
            else:
                if dest.resource == 'sns':
                    msg = event['Records'][0]
                    data = {'bucket': msg['s3']['bucket']['name'],
                            'key': msg['s3']['object']['key']}
                elif dest.resource == 'sqs':
                    data = event
            return f(self, data, context)
        return wrapped_f
    return wrap