import os
from pathlib import Path
from typing import Literal

import click
import semver
import toml

from .constants import SUPPORTED_EXPORT_FORMATS, ExportFormatType
from .scad import ScadInterface

DEFAULT_PROJECT_TOML = """\
[project]
name = "{name}"
version = "0.1.0"
oscar = "0.1.0"

[project.variables]

[project.modules]
"""

DEFAULT_MAIN_CONTENT = """\
include <_parts.scad>

linear_extrude(1)
text(project_version);
"""

DEFAULT_LIB_CONTENT = """\
module dummy() {
    cube([5, 5, 5]);
}
"""

DEFAULT_GITIGNORE_CONTENT = """\
*.stl
*.dxf
*.3mf
oscar.lock
"""


PROJECT_DIRECTORIES = ["src", "build", "modules"]
PROJECT_FILES = {
    "oscar.toml": DEFAULT_PROJECT_TOML,
    ".gitignore": DEFAULT_GITIGNORE_CONTENT,
}


class Project:
    def __init__(self, path: Path, name: str, version: str):
        self.path = path
        self.name = name
        self.version = version
        self.variables = {
            "project_name": f'"{self.name}"',
            "project_version": f'"{self.version}"',
        }
        self.modules = {}
        self.ready = False

    @staticmethod
    def new(name: str, empty: bool = False):
        root = Path.cwd() / name
        if root.exists():
            raise SystemExit(f"Project {name} already exists.")
        root.mkdir(exist_ok=False)
        os.chdir(root)
        project = Project.init(empty=empty)
        return project

    @staticmethod
    def init(empty: bool = False):
        root = Path.cwd()
        name = root.name
        # TODO validate if legal project name (shouldn't have whitespace or special chars)
        for directory in PROJECT_DIRECTORIES:
            (root / directory).mkdir()

        for filename, content in PROJECT_FILES.items():
            (root / filename).write_text(content.format(name=name))

        if not empty:
            (root / "src" / "main.scad").write_text(DEFAULT_MAIN_CONTENT)
            (root / "src" / "_parts.scad").write_text(DEFAULT_LIB_CONTENT)
        return Project.load(root)

    @staticmethod
    def validate_project_dir(path: Path):
        """
        _summary_

        :param path: _description_
        :type path: Path
        :raises RuntimeError: _description_
        :raises RuntimeError: _description_
        """
        for directory in PROJECT_DIRECTORIES:
            if not (path / directory).is_dir():
                raise RuntimeError(
                    f"Failed to load project: {directory} not a directory."
                )
        for filename in PROJECT_FILES:
            if not (path / filename).is_file():
                raise RuntimeError(f"Failed to load project: {filename} not a file.")

    @staticmethod
    def load(path: Path) -> "Project":
        Project.validate_project_dir(path)
        with open(path / "oscar.toml", "r") as f:
            config = toml.load(f)
        name = config["project"]["name"]
        version = config["project"]["version"]
        project = Project(path, name, version)
        if "variables" in config["project"]:
            project.variables.update(config["project"]["variables"])
        project.ready = True
        return project

    def bump(self, value: Literal["major", "minor", "patch"]):
        """
        _summary_

        :param value: _description_
        :type value: Literal[&quot;major&quot;, &quot;minor&quot;, &quot;patch&quot;]
        """
        ver = semver.Version.parse(self.version)
        match value:
            case "major":
                ver.bump_major()
            case "minor":
                ver.bump_minor()
            case "patch":
                ver.bump_patch()
        self.version = str(ver)

    @property
    def source_path(self):
        """
        _summary_

        :return: _description_
        :rtype: _type_
        """
        return self.path / "src"

    @property
    def scad_files(self):
        """
        _summary_

        :return: _description_
        :rtype: _type_
        """
        return sorted(list(self.source_path.glob("*.scad")))

    def build(self, output_format: ExportFormatType = "stl"):
        """
        _summary_

        :param output_format: _description_, defaults to "stl"
        :type output_format: ExportFormatType, optional
        """
        Project.validate_project_dir(self.path)
        scad = ScadInterface()
        source_path = self.path / "src"
        output_path = self.path / "build"
        for input_file in source_path.glob("*.scad"):
            if input_file.name.startswith("_"):
                continue
            click.secho(f"Building file {input_file}...", fg="blue")
            output_filename = (
                output_path / input_file.with_suffix(f".{output_format}").name
            )
            scad.compile(
                input_file,
                output_path=output_filename,
                output_format=output_format,
                variables=self.variables,
                cwd=source_path,
            )
            # TODO increment build counter for part and save value to oscar.lock
            click.secho(
                f"Done building {input_file}, result can be found in {output_filename} .",
                fg="green",
            )

    def clean(self):
        """
        _summary_
        """
        Project.validate_project_dir(self.path)
        output_path = self.path / "build"
        for output_file in output_path.glob("*"):
            if output_file.suffix[1:] in SUPPORTED_EXPORT_FORMATS:
                click.secho(f"Cleaning file {output_file}.", fg="blue")
                output_file.unlink()

    def pack(self, output_path: Path):
        Project.validate_project_dir(self.path)
        raise NotImplementedError

    @staticmethod
    def unpack(path: Path):
        raise NotImplementedError

    def save(self):
        """
        _summary_
        """
        Project.validate_project_dir(self.path)
        config = toml.load(self.path / "oscar.toml")
        config["project"]["modules"] = self.modules
        config["project"]["variables"] = {
            k: v
            for k, v in self.variables.items()
            if k not in ("project_version", "project_name")
        }
        with open(self.path / "oscar.toml", "w") as f:
            toml.dump(config, f)
