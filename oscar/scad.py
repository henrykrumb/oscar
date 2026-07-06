import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

from .constants import SUPPORTED_EXPORT_FORMATS, ExportFormatType


class ScadInterface:
    def __init__(self):
        self.binary = ScadInterface.find_openscad_binary()
        self.version = ScadInterface.openscad_version()

    @staticmethod
    def find_openscad_binary() -> Path:
        """
        Find the OpenSCAD binary on the user's system.

        :raises RuntimeError: If binary could not be found.
        :return: Path to OpenSCAD binary.
        :rtype: Path
        """
        bin = shutil.which("openscad")
        if bin is None:
            raise RuntimeError("OpenSCAD binary not found. Did you install OpenSCAD?")
        bin = Path(bin)
        if not bin.exists():
            raise RuntimeError(
                "OpenSCAD binary does not exist. Did you install OpenSCAD?"
            )
        # TODO allow overrides through config
        return Path(bin)

    @staticmethod
    def openscad_version() -> str:
        """
        Return version string of OpenSCAD system installation.

        :return: Version string, typically YEAR.RELEASE (e.g. 2021.01)
        :rtype: str
        """
        binary = ScadInterface.find_openscad_binary()
        version_string = subprocess.getoutput(f"{binary} --version")
        tokens = version_string.split(" ")
        assert len(tokens) == 3
        version = tokens[2]
        return version

    def edit(
        self,
        input_paths: List[Path],
        variables: Optional[Dict] = None,
        cwd: Optional[Path] = None,
    ):
        """
        Open the OpenSCAD editor inside a specified cwd.

        :param input_paths: _description_
        :type input_paths: List[Path]
        :param variables: _description_, defaults to None
        :type variables: Optional[Dict], optional
        :param cwd: _description_, defaults to None
        :type cwd: Optional[Path], optional
        """
        cmd = [str(self.binary)]
        cmd.extend([str(p) for p in input_paths])
        if variables is not None:
            for k, v in variables.items():
                cmd.extend(["-D", f"{k}={v}"])
        subprocess.run(cmd, cwd=cwd)

    def compile(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        output_format: ExportFormatType | str = "stl",
        ascii: bool = True,
        variables: Optional[Dict] = None,
        cwd: Optional[Path] = None,
    ):
        """
        Use OpenSCAD to compile an input `*.scad` file.

        :param input_path: Path to input scad file.
        :type input_path: Path
        :param output_path: Destination path, defaults to None
        :type output_path: Optional[Path], optional
        :param output_format: Export format, defaults to "stl"
        :type output_format: ExportFormatType | str, optional
        :param ascii: For stl files; whether to export as ASCII, defaults to True
        :type ascii: bool, optional
        :param variables: _description_, defaults to None
        :type variables: Optional[Dict], optional
        :param cwd: Current working directory (relevant for imports/includes), defaults to None
        :type cwd: Optional[Path], optional
        """
        assert output_format in SUPPORTED_EXPORT_FORMATS
        output_path = output_path or input_path.with_suffix(f".{output_format}")
        cmd = [self.binary, str(input_path), "-o", str(output_path)]
        if not ascii and output_format == "stl":
            cmd.extend(["--export-format", "binstl"])
        if variables is not None:
            for k, v in variables.items():
                cmd.extend(["-D", f"{k}={v}"])
        subprocess.run(cmd, cwd=cwd)

    def info(self) -> str:
        """
        Calls `openscad --info` and return its output.

        :return: Info string
        :rtype: str
        """
        cmd = f"{self.binary} --info"
        output = subprocess.getoutput(cmd)
        return output

    @property
    def user_library_path(self) -> Path:
        """
        Get OpenSCAD user-specific library path by issuing a call to `openscad --info`
        and parsing the output.

        :return: Path to OpenSCAD third-party library path.
        :rtype: Path
        """
        info = self.info()
        lines = info.splitlines()
        user_lib_line = [L for L in lines if L.startswith("User Library Path")]
        assert len(user_lib_line) > 0
        user_lib_path = user_lib_line[0].split(": ")[1]
        return Path(user_lib_path)
