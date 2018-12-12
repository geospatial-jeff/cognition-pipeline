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
    entry_points={
        "console_scripts": [
            "create=pipeline._cli.create_pipeline"
        ]
    }
)