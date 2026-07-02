from pathlib import Path

import toml

from .config import MODULE_INDEX_PATH
from .project import Project
from .scad import ScadInterface


class Module:
    def __init__(self, name):
        self.name = name

    @staticmethod
    def load_module_index():
        with open(MODULE_INDEX_PATH, "r") as f:
            module_index = toml.load(f)
        return module_index

    def _git_clone(self, url):
        raise NotImplementedError

    def _download_and_unpack(self, url):
        raise NotImplementedError

    def install(self, destination: Path):
        index = Module.load_module_index()
        module_def = index["modules"][self.name]
        download = module_def["download"]
        if download.endswith(".zip"):
            self._download_and_unpack(download)
            # TODO validate checksum

    def install_system(self):
        project = Project.load(Path.cwd())
        project.modules[self.name] = "global"
        project.save()

        scad = ScadInterface()
        if not scad.user_library_path.is_dir():
            raise RuntimeError("OpenSCAD user library path does not exist.")
        self.install(scad.user_library_path / self.name)

    def install_local(self):
        project = Project.load(Path.cwd())
        project.modules[self.name] = "local"
        project.save()
