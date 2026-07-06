"""
Handle command line arguments and subcommands through `click`.
"""

from pathlib import Path

import click

from .constants import SUPPORTED_EXPORT_FORMATS
from .moduleindex import ModuleIndex
from .project import Project
from .scad import ScadInterface


@click.group(help="oscar: The OpenSCAD Project Manager.")
def cli():
    pass


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(SUPPORTED_EXPORT_FORMATS),
    default="stl",
    help="Export format",
)
def build(format):
    """
    Build an entire project.

    :param format: Export format
    :type format: Legal export format
    """
    project = Project.load(Path.cwd())
    project.build(format)


@cli.command(help="Clean up exported models and images")
def clean():
    """
    Clean up exported models and images.
    """
    project = Project.load(Path.cwd())
    project.clean()


@cli.command(help="Initialize an oscar project inside the current directory")
@click.option(
    "--empty", "-e", is_flag=True, help="Don't populate the project with example files"
)
def init(empty: bool):
    """
    Initialize an OpenSCAD/oscar project inside the current directory.

    :param empty: If true, don't populate the project with example files
    :type empty: bool
    """
    project = Project.init(empty=empty)
    click.secho(f"Project {project.name} created in {project.path}", fg="green")


@cli.command(help="Create a new OpenSCAD project")
@click.option(
    "--empty", "-e", is_flag=True, help="Don't populate the project with example files"
)
@click.argument("name", type=str)
def new(empty: bool, name: str):
    """
    Create a new OpenSCAD project.

    :param empty: If true, don't populate the project with example files
    :type empty: bool
    :param name: Project (and directory) name
    :type name: str
    """
    project = Project.new(name, empty=empty)
    click.secho(f"Project {project.name} created in {project.path}", fg="green")


@cli.command(help="Display info about OpenSCAD system installation.")
def scad():
    """
    Display info about OpenSCAD system installation.
    """
    scad = ScadInterface()
    binary = scad.binary
    version = scad.version
    library_path = scad.user_library_path
    click.secho(f"OpenSCAD binary: {binary}")
    click.secho(f"OpenSCAD version: {version}")
    click.secho(f"OpenSCAD user library path: {library_path}")


@cli.command(help="")
@click.option("--output", "-o", type=click.Path(exists=False))
def pack(output):
    """
    :param output: _description_
    :type output: _type_
    """
    project = Project.load(Path.cwd())
    project.pack(output)


@cli.command(help="")
def unpack():
    """
    """
    raise NotImplementedError()


@cli.command(help="Open the OpenSCAD editor inside the project environment")
# TODO add options that reflect openscad editor options
@click.option("--watch", "-w", is_flag=True)
def edit(watch: bool):
    """
    Open the OpenSCAD editor inside the project environment

    :param watch: _description_
    :type watch: _type_
    """
    project = Project.load(Path.cwd())
    scad = ScadInterface()
    scad.edit(project.scad_files, variables=project.variables, cwd=project.path)


@cli.command(help="Update an oscar project's version")
@click.argument("value", type=click.Choice(["major", "minor", "patch"]))
def bump(value):
    project = Project.load(Path.cwd())
    project.bump(value)


@cli.command(help="Install an indexed OpenSCAD library")
@click.option("--system", "-s", is_flag=True, help="Install in OpenSCAD library path")
@click.option("--reinstall", "-r", is_flag=True, help="Force reinstallation of module and dependencies")
@click.argument("module")
def install(system, reinstall, module):
    index = ModuleIndex()
    if system:
        index.install_system(module, force=reinstall)
    else:
        index.install_local(module, force=reinstall)


@cli.command("index")
@click.option("-d", "--dependencies", is_flag=True)
def index(dependencies):
    index = ModuleIndex()
    module_keys = sorted(list(index.modules.keys()))
    for key in module_keys:
        s = key
        if dependencies and len(index[key].wants) > 0:
            s = f"{key}  -->  {{ "
            s += ", ".join(index[key].wants)
            s += " }"
        print(s)
