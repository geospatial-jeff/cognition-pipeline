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

    def test_sns_bucket_notification(self):
        outfile = 'data/bucket_notification.txt'
        key = "sns/notification.txt"
        response = self.pipeline.functions['sns_bucket_notification'].invoke(outfile, key=key)
        self.assertEqual(response['bucket'], "CognitionPipelineUnittestBucket")
        self.assertEqual(response['key'], key)
        for message in self.pipeline.resources['LoggingQueue'].listen():
            if message.message_attributes['id']['StringValue'] == 'sns_bucket_notification':
                with open(outfile, 'r') as f:
                    contents = f.read()
                    # Strip quotes from message
                    self.assertEqual(message.body[1:-1], contents)
                    message.delete()

    def test_sqs_bucket_notification(self):
        outfile = 'data/bucket_notification.txt'
        key = "sqs/notification.txt"
        response = self.pipeline.functions['sqs_bucket_notification'].invoke(outfile, key=key)
        self.assertEqual(response['bucket'], "CognitionPipelineUnittestBucket")
        self.assertEqual(response['key'], key)
        for message in self.pipeline.resources['LoggingQueue'].listen():
            if message.message_attributes['id']['StringValue'] == 'sqs_bucket_notification':
                with open(outfile, 'r') as f:
                    contents = f.read()
                    # Strip quotes from message
                    self.assertEqual(message.body[1:-1], contents)
                    message.delete()

    def test_sqs(self):
        response = self.pipeline.functions['sqs'].invoke('testing')
        for message in self.pipeline.resources['LoggingQueue'].listen():
            if message.message_attributes['id']['StringValue'] == 'sqs':
                self.assertEqual(message.body[1:-1], 'testing')