# Cognition-Pipeline
Python library for building and testing serverless, event-driven, data processing pipelines with AWS Lambda and Python.

## Overview
Cognition-Pipeline is a python interface to the [Serverless Framework](https://serverless.com/), a widely-adopted toolkit for building serverless applications via configuration yaml files and code snippets.  Cognition-Pipeline abstracts the components of an AWS serverless application to provide an object-oriented interface for building customized data processing pipelines or services with Serverless Framework.  Your code is deployed and executed exactly how its written.

## Example
```python
from pipeline import Pipeline, events

# Simple pipeline with "Hello World" lambda function

class HelloWorldPipeline(Pipeline):

    def __init__(self):
        super().__init__()
       
    @events.invoke
    def hello_world(self, event, context):
        print("Hello World!")

pipeline = HelloWorldPipeline()

hello_world = pipeline.hello_world

def deploy():
    pipeline.deploy()
```

## Quickstart
1. Install library: \
```pip install git+https://github.com/geospatial-jeff/cognition-pipeline.git``` \
2. Create a new pipeline in a new directory: \
```pipeline-create <new-directory>```
3. Build your pipeline in the `<new-directyr>/handler.py` script.  You may add:
    - **Lambda Functions:** Create a new lambda function by creating a new Pipeline method.
    - **Events:** Configure the lambda function's event trigger with decorators.
    - **Resources:** Configure other AWS resources (SQS, SNS etc.) used by your Pipeline.
4. Deploy your pipeline to AWS via Serverless Framework  \
```pipeline-deploy <new-directory>```

## Testing
1. Deploy test pipeline to AWS with `pipeline-deploy tests`
2. Run the unittests in `tests/tests.py`