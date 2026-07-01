from pathlib import Path

import click

from .constants import SUPPORTED_EXPORT_FORMATS
from .project import Project
from .scad import ScadInterface


@click.group(help="oscar: The OpenSCAD Project Manager.")
def cli():
    pass


@cli.command(help="Build the entire project")
@click.option(
    "--format", "-f", type=click.Choice(SUPPORTED_EXPORT_FORMATS), default="stl"
)
def build(format):
    project = Project.load(Path.cwd())
    project.build()


@cli.command(help="Clean up exported models and images.")
def clean():
    project = Project.load(Path.cwd())
    project.clean()


@cli.command(help="Create a new OpenSCAD project.")
@click.argument("name")
def init(name):
    project = Project.init(name)
    click.secho(f"Project {name} created in {project.path}", fg="green")


@cli.command(help="Display info about OpenSCAD system installation.")
def scad():
    scad = ScadInterface()
    binary = scad.binary
    version = scad.version
    click.secho(f"OpenSCAD binary: {binary}")
    click.secho(f"OpenSCAD version: {version}")


@cli.command()
def watch():
    raise NotImplementedError()


@cli.command()
@click.option("--output", "-o", type=click.Path(exists=False))
def pack(output):
    project = Project.load(Path.cwd())
    project.pack(output)


@cli.command()
def unpack():
    raise NotImplementedError()
