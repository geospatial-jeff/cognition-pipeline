import json

from pipeline import Pipeline, events, resources

class SNSTopicTest(resources.SNSTopic):

    def __init__(self):
        super().__init__()

class SQSQueueTest(resources.SQSQueue):

    def __init__(self):
        super().__init__()

class SQSQueueTest2(resources.SQSQueue):

    def __init__(self):
        super().__init__()

class LoggingQueue(resources.SQSQueue):

    def __init__(self):
        super().__init__()

class DynamoDBTest(resources.DynamoDB):

    def __init__(self):
        super().__init__()
        self.add_attribute('id', 'S')
        self.add_key('id', 'HASH')

class CognitionPipelineUnittestBucket(resources.S3Bucket):

    def __init__(self):
        super().__init__()

testing_topic = SNSTopicTest()
testing_queue = SQSQueueTest()
testing_queue2 = SQSQueueTest2()
logging_queue = LoggingQueue()
testing_table = DynamoDBTest()
testing_bucket = CognitionPipelineUnittestBucket()

class MyPipeline(Pipeline):

    def __init__(self):
        super().__init__(name="pipeline-unittests",
                         resources=[testing_topic, testing_bucket, testing_queue,
                                    testing_queue2, logging_queue, testing_table])

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

    @events.sns(resource=testing_topic)
    def sns(self, event, context):
        logging_queue.send_message(event, id="sns")

    @events.bucket_notification(bucket=testing_bucket, event_type="s3:ObjectCreated:Put", destination=testing_topic, prefix="sns")
    def sns_bucket_notification(self, event, context):
        contents = testing_bucket.read_file(event['key'])
        # Send the contents of file to SQS queue so we can check the output clientside
        logging_queue.send_message(contents, id="sns_bucket_notification")

    @events.bucket_notification(bucket=testing_bucket, event_type="s3:ObjectCreated:Put", destination=testing_queue, prefix="sqs")
    def sqs_bucket_notification(self, event, context):
        contents = testing_bucket.read_file(event['key'])
        # Send the contents of file to SQS queue so we can check the output clientside
        logging_queue.send_message(contents, id="sqs_bucket_notification")

    @events.sqs(resource=testing_queue2)
    def sqs(self, event, context):
        # Send the contents of message to SQS queue so we can check the output clientside
        logging_queue.send_message(event, id="sqs")

    @events.invoke
    def sqs_aggregate(self, event, context):
        for x in event['sequence']:
            logging_queue.send_message(str(x), id="sqs_aggregate")

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

def sns(event, context):
    pipeline.sns(event, context)

def sns_bucket_notification(event, context):
    pipeline.sns_bucket_notification(event, context)

def sqs_bucket_notification(event, context):
    pipeline.sqs_bucket_notification(event, context)

def sqs(event, context):
    pipeline.sqs(event, context)

def sqs_aggregate(event, context):
    pipeline.sqs_aggregate(event, context)


def deploy():
    pipeline.deploy()