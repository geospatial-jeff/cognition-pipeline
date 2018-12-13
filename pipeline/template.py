from pipeline import Pipeline
from pipeline.resources import SNSTopic
from pipeline import events

from pipeline.services import UploadFile

"""Define resources"""

class MyTopic(SNSTopic):

    def __init__(self):
        super().__init__()

"""Create the pipeline"""

class MyPipeline(Pipeline):

    def __init__(self):
        super().__init__(name="my-test-pipeline",
                         resource=[MyTopic],
                         services=[UploadFile])

    @events.sns(resource=MyTopic)
    def my_lambda(self, event, context):
        UploadFile().execute(event, context)

pipeline = MyPipeline()

"""Define lambda functions"""

def my_lambda(event, context):
    pipeline.my_lambda(event, context)

def deploy():
    pipeline.deploy()