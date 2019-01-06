import yaml


class Outputs(dict):
    @classmethod
    def load(cls, fname):
        with open(fname, "r") as stream:
            contents = yaml.load(stream)
            return cls(contents)

    def __init__(self, contents):
        super().__init__()
        self.update(contents)

    def endpoint(self):
        if "ServiceEndpoint" in self.keys():
            return self["ServiceEndpoint"]
        else:
            return None

    def deployment_bucket(self):
        return self["ServerlessDeploymentBucketName"]

    def functions(self):
        if "functions" in self.keys():
            return self["functions"]
        else:
            return None
