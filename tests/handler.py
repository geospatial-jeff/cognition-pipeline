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

    @events.http(path="get/{id}", method="get", cors="true")
    def http_get(self, event, context):
        response = {'statusCode': '200',
                    'body': event['id']}
        return response

    @events.http(path="post", method="post", cors="true")
    def http_post(self, event, context):
        response = {'statusCode': '200',
                    'body': json.dumps(event)}
        return response


pipeline = MyPipeline()

def invoke(event, context):
    resp = pipeline.invoke(event, context)
    return resp

def http_get(event, context):
    resp = pipeline.http_get(event, context)
    return resp

def http_post(event, context):
    resp = pipeline.http_post(event, context)
    return resp

def deploy():
    pipeline.deploy()