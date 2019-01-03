from setuptools import setup, find_packages

with open("./requirements.txt") as reqs:
    requirements = [line.rstrip() for line in reqs]

setup(
    name="cognition_pipeline",
    version="0.1",
    description="Build and deploy AWS serverless pipelines",
    author="Jeff Albrecht",
    author_email="geospatialjeff@gmail.com",
    packages=find_packages(),
    install_requires=requirements,
    exclude=["examples"],
    entry_points={
        "console_scripts": [
            "pipeline-create=pipeline._cli:create_pipeline",
            "pipeline-deploy=pipeline._cli:deploy_pipeline"
        ]
    }
)