import unittest
import boto3
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



test_cases = MyPipelineTestCases()