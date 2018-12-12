import json

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