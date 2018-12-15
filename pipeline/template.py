from pipeline import Pipeline, events


class MyPipeline(Pipeline):

    def __init__(self):
        super().__init__(name="my-pipeline")


    @events.invoke
    def my_lambda(self, event, context):
        print("Hello world!")

pipeline = MyPipeline()


"""Lambda handlers"""

def my_lambda(event, context):
    pipeline.my_lambda(event, context)


"""Deploy pipeline"""

def deploy():
    pipeline.deploy()