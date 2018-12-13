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
                                        Payload=json.dumps(data)
                                        )
        return response

class FunctionGroup(object):

    @classmethod
    def load_functions(cls, func_names, pipeline):
        loaded = {}
        pipeline.mode = "deploy"
        for item in func_names:
            short_name = item.split('-')[-1]
            info = getattr(pipeline, short_name)(None, None)
            loaded.update({short_name: Function(item, info)})
        pipeline.mode = "deployed"
        return cls(loaded)

    def __getitem__(self, item):
        return self.all[item]

    def __init__(self, functions):
        self.all = functions

    def to_dict(self):
        dicts = [self.all[k].info for k in self.all.keys()]
        return dicts