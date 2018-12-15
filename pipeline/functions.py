import boto3
import json

lambda_client = boto3.client('lambda')

class Function(object):

    def __init__(self, name, info):
        self.name = name
        self.info = info

    def invoke(self, data, invocation="Event"):
        response = lambda_client.invoke(FunctionName=self.name,
                                        InvocationType=invocation,
                                        Payload=json.dumps(data))
        return response

class FunctionGroup(object):

    @staticmethod
    def load(func, pipeline):
        func_name = func.__name__
        event = func.id
        func_info = {"handler": 'handler.'+func_name}
        if event == 'lambda':
            return {func_name: Function(func_name, func_info)}
        elif event == 'http':
            func_info.update({
                "events": [
                    {
                        "http": {
                            "path": func.args['path'],
                            "method": func.args['method'],
                            "cors": func.args['cors']
                        }
                    }
                ]
            })
            return {func_name: Function(func_name, func_info)}
        elif event == 'sns':
            func_info.update({
                "events": [
                    {
                        "sns": {
                            "arn": pipeline.resources[func.args['topic_name']].arn,
                            "topicName": func.args['topic_name'],
                        }
                    }
                ]
            })
            return {func_name: Function(func_name, func_info)}


    @classmethod
    def load_functions(cls, func_names, pipeline):
        loaded = {}
        for item in func_names:
            func = getattr(pipeline, item)
            info = cls.load(func, pipeline)
            loaded.update(info)
        return cls(loaded)

    def __getitem__(self, item):
        return self.all[item]

    def __init__(self, functions):
        self.all = functions

    def to_dict(self):
        # dicts = [self.all[k].info for k in self.all.keys()]
        dicts = [{k:self.all[k].info} for k in self.all.keys()]
        return dicts