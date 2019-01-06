import os
import sys
import click
import subprocess
from shutil import copyfile


@click.command()
@click.argument("name")
def create_pipeline(name):
    """Create a template pipeline in a specified directory"""

    if not os.path.exists(name):
        os.makedirs(name)

    # Create requirements
    with open(os.path.join(name, "requirements.txt"), "a") as reqs:
        reqs.write("git+https://github.com/geospatial-jeff/cognition-pipeline.git\n")

    # Copy template project into directory
    template = os.path.join(os.path.dirname(os.path.realpath(__file__)), "template.py")
    copyfile(template, os.path.join(name, "handler.py"))


@click.command()
@click.argument("name")
@click.option("--dry-run", default=False, is_flag=True)
def deploy_pipeline(name, dry_run):
    """Deploy the pipeline in a specified directory (creates serverless.yml)"""
    os.chdir(name)
    sys.path.append(os.getcwd())
    import handler

    handler.deploy()
    if not dry_run:
        subprocess.call(
            "sls plugin install -n serverless-python-requirements", shell=True
        )
        subprocess.call("sls deploy -v", shell=True)
        subprocess.call("sls info -v --force > outputs.txt", shell=True)
        parse_output()


def parse_output():
    with open("outputs.yml", "w") as outfile:
        with open("outputs.txt", "r") as infile:
            lines = infile.readlines()
            for idx, line in enumerate(lines):
                if line == "Service Information\n" or line == "Stack Outputs\n":
                    lines.pop(idx)
                else:
                    outfile.write(line)
    os.remove("outputs.txt")


# if __name__ == "__main__":
# create_pipeline()
# deploy_pipeline()
