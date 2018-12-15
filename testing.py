from pipeline import Pipeline
from pipeline import resources, events
from pipeline import execution

class MyTopic(resources.SNSTopic):

    def __init__(self):
        super().__init__()

class MyPipeline(Pipeline):

    def __init__(self):
        super().__init__(name="my-pipeline",
                         resource=[MyTopic])


    @events.sns(resource=MyTopic())
    def my_lambda(self, event, context):
        pass

test = MyPipeline()
test.deploy()