import unittest

from handler import pipeline

class ResourceTestCases(unittest.TestCase):

    def setUp(self):
        self.sns_topic = pipeline.resources['SNSTopicTest']
        self.sqs_queue = pipeline.resources['LoggingQueue']
        self.s3_bucket = pipeline.resources['CognitionPipelineUnittestBucket']

    def check_response(self, response):
        self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_sns_send_message(self):
        response = self.sns_topic.send_message('test_message')
        self.check_response(response)

    def test_sqs(self):
        response = self.sqs_queue.send_message('test_message', id="sqs_resource_test")
        self.check_response(response)

        for message in self.sqs_queue.listen():
            uid = message.message_attributes['id']['StringValue']
            if uid == 'sqs_resources_test':
                self.assertEqual(message.body[1:-1], 'test_message')
            message.delete()

    def test_s3_read_file(self):
        response = self.s3_bucket.read_file('resource_test/upload_file.txt')
        with open('data/bucket_notification.txt', 'r') as f:
            contents = f.read()
            self.assertEqual(response, contents)

    def test_s3_upload_file(self):
        x = 0
        with open('data/bucket_notification.txt', 'r') as f:
            contents = f.read()
            try:
                self.s3_bucket.upload_file('resource_test/upload_file.txt', contents)
                x+=1
            except:
                pass
        self.assertEqual(x,1)