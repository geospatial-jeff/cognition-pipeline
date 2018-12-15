import os
import sys
import click
import subprocess
from shutil import copyfile

@click.command()
@click.argument("name")
def create_pipeline(name):

    if not os.path.exists(name):
        os.makedirs(name)

    # Create requirements
    with open(os.path.join(name, 'requirements.txt'), 'a') as reqs:
        reqs.write('git+https://github.com/geospatial-jeff/cognition-pipeline.git\n')

    # Copy template project into directory
    template = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template.py')
    copyfile(template, os.path.join(name, 'handler.py'))

@click.command()
@click.argument("name")
def deploy_pipeline(name):
    os.chdir(name)
    sys.path.append(os.getcwd())
    import handler
    handler.deploy()

if __name__ == "__main__":
    # create_pipeline()
    deploy_pipeline()