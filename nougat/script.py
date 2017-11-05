import click
import pkg_resources
import os
import sys
import json


@click.group()
def cli():
    """
    Nougat, API framework
    """
    sys.path.append(os.getcwd())


@cli.command(short_help='build the document')
@click.argument('src')
@click.option("--output", type=click.File('w'), default="api.json", help="the place where api document save")
def doc(src, output):
    """

    """
    try:
        app = pkg_resources.EntryPoint.parse("app={}".format(src)).load(False)
        output.write(json.dumps(app.doc(), indent=4))
    except ModuleNotFoundError:
        click.echo("project entry point is incorrect")
    except ImportError:
        click.echo("Nougat Instance entry point is incorrect")
