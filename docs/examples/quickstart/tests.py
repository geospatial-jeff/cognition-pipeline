import unittest
import json
import time

from handler import pipeline

class MyFirstPipelineTestCases(unittest.TestCase):

    def setUp(self):
        self.pipeline = pipeline

    def test_hello_world(self):
        func = self.pipeline.functions['hello_world']
        table = self.pipeline.resources['QuickstartTable']
        # Invoke your lambda function (creates a new entry in DynamoDB Table)
        func.invoke('test_entry')
        # Give the table some time to update
        time.sleep(5)
        # Confirm the new entry using a DynamoDB table scan
        response = table.list()
        self.assertEqual(len(response), 1)
        self.assertEqual(response[0]['message'], 'test_entry')
        # Delete the new entry with the entry's id
        table.delete(response[0]['id'])