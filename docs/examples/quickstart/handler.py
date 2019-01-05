import uuid
import json

from pipeline import Pipeline, events, resources

"""Define resources"""

class MyTable(resources.DynamoDB):

    def __init__(self):
        super().__init__()
        self.add_attribute('id', 'S')
        self.add_key('id', 'HASH')

table = MyTable()

"""Build pipeline"""

class MyFirstPipeline(Pipeline):

    def __init__(self):
        super().__init__(name="my-first-pipeline",
                         resources=[table])

    @events.http(method="get", path="helloworld/{message}", cors="true")
    def hello_world(self, event, context):
        item = {'id': str(uuid.uuid1),
                'message': event['message']
                }
        # Use helper method
        table.put(item)

    @events.http(method="get", path="helloworld", cors="true")
    def list_messages(self, event, context):
        messages = table.list()
        resp = {'statusCode': 200,
                'body': json.dumps(messages)}
        return messages


pipeline = MyFirstPipeline()

"""Lambda handlers"""

def hello_world(event, context):
    pipeline.hello_world(event, context)


def list_messages(event, context):
    resp = pipeline.list_messages(event, context)
    return resp

"""Deploy"""

def deploy():
    pipeline.deploy()