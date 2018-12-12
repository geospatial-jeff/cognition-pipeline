import os
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
    copyfile(template, os.path.join(name, "handler.py"))

@click.command()
@click.argument("name")
def deploy_pipeline(name):

    os.chdir(name)
    subprocess.Popen('python handler.py && sls plugin install -n serverless-python-requirements && sls deploy -v', shell=True)

# if __name__ == "__main__":
#     deploy_pipeline()
#     # create_pipeline()