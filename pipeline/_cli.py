import os
import click
from shutil import copyfile

@click.command()
@click.option("--name", help="Name of pipeline directory")

def create_pipeline(name):

    if not os.path.exists(name):
        os.makedirs(name)

    # Create requirements
    with open(os.path.join(name, 'requirements.txt'), 'a') as reqs:
        reqs.write('git+https://github.com/geospatial-jeff/cognition-pipeline.git')

    # Copy template project into directory
    template = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'template.py')
    copyfile(template, os.path.join(name, "pipeline.py"))