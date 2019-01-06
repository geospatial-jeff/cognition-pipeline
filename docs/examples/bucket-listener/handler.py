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

class BucketListenerExample(Pipeline):

    def __init__(self):
        super().__init__(resources=[bucket, bucket_listener])

    @events.bucket_notification(bucket=TargetBucketTesting123(), event_type="s3:ObjectCreated:Put", destination=BucketListener())
    def print_fname(self, event, context):
        print(f"A file was uploaded to {os.path.join(event['bucket'], event['key'])}")

    @events.sns(resource=BucketListener())
    def read_file(self, event, context):
        contents = bucket.read_file(event['key'])
        print(contents)

pipeline = BucketListenerExample()


"""Lambda handlers"""

print_fname = pipeline.print_fname
read_file = pipeline.read_file


"""Deploy pipeline"""

def deploy():
    pipeline.deploy()