import os
from pathlib import Path
from typing import Literal

import click
import semver
import toml

from .constants import SUPPORTED_EXPORT_FORMATS, ExportFormatType
from .scad import ScadInterface
from .utils import parse_scad_shebang

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
        self.version = semver.Version.parse(version)
        self.variables = {
            "project_name": f'"{self.name}"',
            "project_version": f'"{str(self.version)}"',
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
        if os.environ.get("OPENSCADPATH") is not None:
            os.environ["OPENSCADPATH"] = ":".join(
                [os.environ["OPENSCADPATH"], str(project.modules_path)]
            )
        else:
            os.environ["OPENSCADPATH"] = str(project.modules_path)
        project.ready = True
        return project

    def bump(self, value: Literal["major", "minor", "patch"]):
        """
        Bump version of oscar project.

        :param value: Which of the parts of the semver string should be bumped.
        :type value: Literal[&quot;major&quot;, &quot;minor&quot;, &quot;patch&quot;]
        """
        match value:
            case "major":
                self.version.bump_major()
            case "minor":
                self.version.bump_minor()
            case "patch":
                self.version.bump_patch()
        self.save()

    @property
    def source_path(self):
        """
        _summary_

        :return: _description_
        :rtype: _type_
        """
        return self.path / "src"

    @property
    def modules_path(self):
        return self.path / "modules"

    @property
    def scad_files(self):
        """
        _summary_

        :return: _description_
        :rtype: _type_
        """
        return sorted(list(self.source_path.glob("*.scad")))

    def build(self, output_format: ExportFormatType | str = "stl"):
        """
        Build all *.scad files in src/ directory and save resulting models to build/ directory.

        :param output_format: Export format supported by OpenSCAD, defaults to "stl"
        :type output_format: ExportFormatType | str, optional
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
            config_override = parse_scad_shebang(input_file)
            output_format = config_override.get("export-format", output_format)
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
        Clean up build directory.
        """
        Project.validate_project_dir(self.path)
        output_path = self.path / "build"
        for output_file in output_path.glob("*"):
            if output_file.suffix[1:] in SUPPORTED_EXPORT_FORMATS:
                click.secho(f"Cleaning file {output_file}.", fg="blue")
                output_file.unlink()

    def save(self):
        """
        Save changes made by CLI commands back to oscar.toml, e.g. when version was bumped.
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

    def pack(self, output_path: Path):
        Project.validate_project_dir(self.path)
        raise NotImplementedError

    @staticmethod
    def unpack(path: Path):
        raise NotImplementedError
