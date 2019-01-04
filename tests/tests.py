import unittest
import boto3
import os
import json

from handler import MyPipeline

lambda_client = boto3.client('lambda')

class MyPipelineTestCases(unittest.TestCase):

    def setUp(self):
        self.pipeline = MyPipeline()

    def test_invoke(self):
        message = {"hello": "world"}
        response = self.pipeline.functions['invoke'].invoke(message)
        self.assertEqual(message, json.loads(response['body']))

    def test_http_get(self):
        id = "test-id"
        response = self.pipeline.functions['http_get'].invoke(id)
        self.assertEqual(response, id)

    def test_http_post(self):
        payload = {"hello": "world",
                   "testing": "123"}
        response = self.pipeline.functions['http_post'].invoke(json.dumps(payload))
        self.assertEqual(payload, json.loads(response))

    def test_sns(self):
        response = self.pipeline.functions['sns'].invoke('testing')
        self.assertEqual(response['ResponseMetadata']['HTTPStatusCode'], 200)

    def test_sns_s3(self):
        outfile = 'data/bucket_notification.txt'
        response = self.pipeline.functions['sns_bucket_notification'].invoke(outfile)
        self.assertEqual(response['bucket'], "CognitionPipelineTestBucket")
        self.assertEqual(response['key'], os.path.split(outfile)[-1])
        for message in self.pipeline.resources['TestingQueue'].listen():
            if message.message_attributes['id']['StringValue'] == 'sns_bucket_notification':
                with open(outfile, 'r') as f:
                    contents = f.read()
                    # Strip quotes from message
                    self.assertEqual(message.body[1:-1], contents)
                    message.delete()