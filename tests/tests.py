import unittest
import boto3
import json

from handler import MyPipeline

lambda_client = boto3.client('lambda')

class MyPipelineTestCases(unittest.TestCase):

    def setUp(self):
        self.pipeline = MyPipeline()

    def test_invoke(self, response=None):
        message = {"hello": "world"}
        response = self.pipeline.functions['invoke'].invoke(message)
        self.assertEqual(message, json.loads(response['body']))

test_cases = MyPipelineTestCases()