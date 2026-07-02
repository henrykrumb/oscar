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


@cli.command(help="Initialize an OpenSCAD/oscar project inside the current directory.")
@click.option(
    "--empty", "-e", is_flag=True, help="Don't populate the project with example files"
)
def init(empty):
    project = Project.init(empty=empty)
    click.secho(f"Project {project.name} created in {project.path}", fg="green")


@cli.command(help="Create a new OpenSCAD project and cd to it.")
@click.option(
    "--empty", "-e", is_flag=True, help="Don't populate the project with example files"
)
@click.argument("name")
def new(empty, name):
    project = Project.new(name, empty=empty)
    click.secho(f"Project {project.name} created in {project.path}", fg="green")


@cli.command(help="Display info about OpenSCAD system installation.")
def scad():
    scad = ScadInterface()
    binary = scad.binary
    version = scad.version
    click.secho(f"OpenSCAD binary: {binary}")
    click.secho(f"OpenSCAD version: {version}")


@cli.command()
@click.option("--output", "-o", type=click.Path(exists=False))
def pack(output):
    project = Project.load(Path.cwd())
    project.pack(output)


@cli.command()
def unpack():
    raise NotImplementedError()


@cli.command("Open the OpenSCAD editor inside the project environment")
# TODO options that reflect openscad editor options
@click.option("--watch", "-w", is_flag=True)
def edit():
    project = Project.load(Path.cwd())
    scad = ScadInterface()
    scad.edit(project.scad_files, variables=project.variables, cwd=project.path)
