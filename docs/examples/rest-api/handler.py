import uuid
import time
import json

from pipeline import Pipeline, events, resources
from .utils import DecimalEncoder

"""Define resources"""


class MyFirstTable(resources.DynamoDB):
    def __init__(self):
        super().__init__()
        self.add_attribute("id", "S")
        self.add_key("id", "HASH")


table = MyFirstTable()

"""Create pipeline"""


class SimpleRestAPI(Pipeline):
    def __init__(self):
        super().__init__(resources=[table])

    @events.http(path="todos", method="post", cors="true")
    def create(self, event, context):
        timestamp = int(time.time() * 1000)
        item = {
            "id": str(uuid.uuid1()),
            "text": event["text"],
            "checked": False,
            "createdAt": timestamp,
            "updatedAt": timestamp,
        }
        table.put(item)

        response = {"statusCode": 200, "body": json.dumps(item)}
        return response

    @events.http(path="todos", method="get", cors="true")
    def list(self, event, context):
        result = table.list()

        response = {"statusCode": 200, "body": json.dumps(result, cls=DecimalEncoder)}
        return response

    @events.http(path="todos/{id}", method="get", cors="true")
    def get(self, event, context):
        result = table.get(event["id"])

        response = {"statusCode": 200, "body": json.dumps(result, cls=DecimalEncoder)}

        return response

    @events.http(path="todos/{id}", method="delete", cors="true")
    def delete(self, event, context):
        table.delete(event["id"])
        response = {"statusCode": 200}
        return response


pipeline = SimpleRestAPI()

"""Lambda handlers"""

create = pipeline.create
list = pipeline.list
get = pipeline.get
delete = pipeline.delete

"""Deploy pipeline"""


def deploy():
    pipeline.deploy()
