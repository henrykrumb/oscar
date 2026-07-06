import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import urlsplit

import click
import requests
from git import RemoteProgress, Repo
from tqdm import tqdm

from .project import Project
from .scad import ScadInterface


class ProgressPrinter(RemoteProgress):
    def __init__(self):
        super().__init__()
        self.tqdm = tqdm()

    def update(self, op_code, cur_count, max_count=None, message=""):
        if self.tqdm.total is None:
            self.tqdm.total = max_count
        assert isinstance(cur_count, float)
        self.tqdm.update(cur_count)
        self.tqdm.display()


class Module:
    def __init__(
        self,
        name: str,
        wants: List[str],
        download: Optional[str] = None,
        clone: Optional[str] = None,
        license: Optional[str] = None,
    ):
        self.name = name
        self.wants = wants
        assert (download is None) ^ (clone is None)
        self.download = download
        self.clone = clone
        self.license = license

    @staticmethod
    def from_dict(key: str, d: Dict[str, Any]) -> "Module":
        name = d.get("name", key)
        wants = d.get("wants", [])
        download = d.get("download")
        clone = d.get("clone")
        license = d.get("license")
        return Module(name, wants, download, clone, license)

    def get_installation_path(self) -> Path | None:
        project = Project.load(Path.cwd())
        if (project.path / self.name).exists():
            return project.path / self.name
        scad = ScadInterface()
        if not scad.user_library_path.is_dir():
            raise RuntimeError("OpenSCAD user library path does not exist.")
        if (scad.user_library_path / self.name).exists():
            return scad.user_library_path / self.name
        return None

    def is_installed(self) -> bool:
        if self.get_installation_path() is None:
            return False
        return True

    def _git_clone(self, destination: Path, force: bool = True):
        assert self.clone is not None
        if force and destination.exists():
            shutil.rmtree(destination)
        Repo.clone_from(self.clone, destination, progress=ProgressPrinter())

    def _download_and_unpack_zip(self, destination):
        assert self.download is not None
        parts = urlsplit(self.download)
        filename = destination / ".." / parts.path.split("/")[-1]
        with requests.get(self.download, stream=True) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in tqdm(
                    r.iter_content(chunk_size=1024),
                    total=int(r.headers.get("content-length", 0)) // 1024,
                    unit="KB",
                ):
                    f.write(chunk)
            shutil.unpack_archive(filename, destination)
            filename.unlink()

    def _download_scad(self, destination: Path):
        assert self.download is not None
        parts = urlsplit(self.download)
        filename = destination / parts.path.split("/")[-1]
        with requests.get(self.download, stream=True) as r:
            r.raise_for_status()
            with open(filename, "wb") as f:
                for chunk in tqdm(
                    r.iter_content(chunk_size=1024),
                    total=int(r.headers.get("content-length", 0)) // 1024,
                    unit="KB",
                ):
                    f.write(chunk)

    def install(self, destination: Path, force: bool = True):
        if destination.exists() and not force:
            click.secho(f"Module {self.name} already installed.", fg="green")
            return
        destination.mkdir(parents=True, exist_ok=True)
        if self.download is not None:
            if self.download.endswith(".zip"):
                self._download_and_unpack_zip(destination)
                # TODO validate checksum
            elif self.download.endswith(".scad"):
                self._download_scad(destination)
        elif self.clone is not None:
            self._git_clone(destination, force=force)
        click.secho(f"Module {self.name} installed.", fg="green")

    def install_system(self, force: bool = True):
        project = Project.load(Path.cwd())
        project.modules[self.name] = "global"
        project.save()
        scad = ScadInterface()
        if not scad.user_library_path.is_dir():
            raise RuntimeError("OpenSCAD user library path does not exist.")
        destination = scad.user_library_path / self.name
        self.install(destination, force=force)

    def install_local(self, force: bool = True):
        project = Project.load(Path.cwd())
        project.modules[self.name] = "local"
        project.save()
        destination = project.path / "modules" / self.name
        self.install(destination, force=force)
