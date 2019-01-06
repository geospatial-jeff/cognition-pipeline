import unittest

from handler import PipelineUnittests

class PipelineDeployTestCases(unittest.TestCase):

    """
    For now just testing if deploy doesn't throw error
    """

    def setUp(self):
        self.pipeline = PipelineUnittests()

    def test_deploy(self):
        x = 0
        try:
            self.pipeline.deploy()
            x+=1
        except:
            raise
        self.assertEqual(x,1)