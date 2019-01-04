import json

from pipeline import Pipeline, events


class MyPipeline(Pipeline):

    def __init__(self):
        super().__init__(name="cognition-pipeline-test-cases")

    @events.invoke
    def invoke(self, event, context):

        response = {'statusCode': '200',
                    'body': json.dumps(event)}
        return response

pipeline = MyPipeline()

def invoke(event, context):
    resp = pipeline.invoke(event, context)
    return resp

def deploy():
    pipeline.deploy()