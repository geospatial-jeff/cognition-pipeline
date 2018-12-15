import boto3

class UploadFile(object):

    @classmethod
    def execute(cls, event, context):
        s3 = boto3.resource('s3')
        object = s3.Object(event['bucket'], event['key'])
        object.put(Body=event['data'])

    @classmethod
    def requirements(cls):
        return ["boto3>=1.9.62"]
