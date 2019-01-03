import os

from pipeline import Pipeline, events, resources

"""Define resources"""

class BucketListener(resources.SNSTopic):

    """Create an SNS Topic which will be listening for a bucket notification"""

    def __init__(self):
        super().__init__()

class TargetBucketTesting123(resources.S3Bucket):

    """Create the target bucket"""

    def __init__(self):
        super().__init__()

bucket = TargetBucketTesting123()
bucket_listener = BucketListener()

class MyPipeline(Pipeline):

    def __init__(self):
        super().__init__(name="bucket-listener-example",
                         resources=[bucket, bucket_listener])

    @events.bucket_notification(bucket=TargetBucketTesting123(), event_type="s3:ObjectCreated:Put", destination=BucketListener())
    def print_fname(self, event, context):
        print(f"A file was uploaded to {os.path.join(event['bucket'], event['key'])}")

    @events.sns(resource=BucketListener())
    def read_file(self, event, context):
        contents = bucket.read_file(event['key'])
        print(contents)

pipeline = MyPipeline()


"""Lambda handlers"""

def print_fname(event, context):
    pipeline.print_fname(event, context)

def read_file(event, context):
    pipeline.read_file(event, context)


"""Deploy pipeline"""

def deploy():
    pipeline.deploy()