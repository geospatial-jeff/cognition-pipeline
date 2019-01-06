import uuid
import json

from pipeline import Pipeline, events, resources

"""Define resources"""


class QuickstartTable(resources.DynamoDB):
    def __init__(self):
        super().__init__()
        self.add_attribute("id", "S")
        self.add_key("id", "HASH")


table = QuickstartTable()

"""Build pipeline"""


class QuickstartPipeline(Pipeline):
    def __init__(self):
        super().__init__(resources=[table])

    @events.http(method="get", path="helloworld/{message}", cors="true")
    def hello_world(self, event, context):
        item = {"id": str(uuid.uuid1()), "message": event["message"]}
        # Use helper method
        table.put(item)

    @events.http(method="get", path="helloworld", cors="true")
    def list_messages(self, event, context):
        messages = table.list()
        resp = {"statusCode": 200, "body": json.dumps(messages)}
        return messages


pipeline = QuickstartPipeline()

"""Lambda handlers"""

hello_world = pipeline.hello_world
list_messages = pipeline.list_messages

"""Deploy"""


def deploy():
    pipeline.deploy()
