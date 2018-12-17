
class Trigger(object):

    def __init__(self, info):
        self.name = self.__class__.__name__.lower()
        self.info = info

class SNS(Trigger):

    def __init__(self, info):
        super().__init__(info)

    def template(self):
        return {
            "events": [
                {
                    "sns": {
                        "arn": self.info['arn'],
                        "topicName": self.info['topic_name']
                    }
                }
            ]
        }

class LAMBDA(Trigger):

    def __init__(self, info):
        super().__init__(info)

    def template(self):
        return None

class HTTP(Trigger):

    def __init__(self, info):
        super().__init__(info)

    def template(self):
        return {
            "events": [
                {
                    "http": {
                        "path": self.info['path'],
                        "method": self.info['method'],
                        "cors": self.info['cors']
                    }
                }
            ]
        }

class SQS(Trigger):

    def __init__(self, info):
        super().__init__(info)

    def template(self):
        return {
            "events": [
                {
                    "sqs": {
                        "arn": self.info['arn'],
                    }
                }
            ]
        }

class BUCKET_NOTIFICATION(Trigger):

    def __init__(self, info):
        super().__init__(info)

    def template(self):
        event_type = self.info['destination'].resource
        if event_type == 'sns':
            return {
                "events": [
                    {
                        "sns": {
                            "arn": self.info['destination'].arn,
                            "topicName": self.info['destination'].name
                        }
                    }
                ]
            }
        elif event_type == 'sqs':
            return {
                "events": [
                    {
                        "sqs": {
                            "arn": self.info['destination'].arn,
                        }
                    }
                ]
            }