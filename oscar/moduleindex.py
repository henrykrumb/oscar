from typing import List

import click
import toml

from .config import MODULE_INDEX_PATH
from .module import Module


class ModuleIndex:
    def __init__(self):
        self._load()

    def _load(self):
        with open(MODULE_INDEX_PATH, "r") as f:
            module_index = toml.load(f)
        module_defs = module_index["modules"]
        self.modules = {
            key: Module.from_dict(key, value) for key, value in module_defs.items()
        }

    def __getitem__(self, key) -> Module:
        if key not in self.modules:
            raise RuntimeError(f"Module {key} not in index.")
        return self.modules[key]

    def _get_dependency_tree(self, module: "Module") -> List["Module"]:
        dependencies = [self[w] for w in module.wants]
        changed = True
        iterations = 0  # avoid an endless loop
        while changed:
            iterations = iterations + 1
            if iterations > 1e4:
                raise RuntimeError("Something went terribly wrong.")
            changed = False
            for d in dependencies:
                for w in d.wants:
                    if w in dependencies:
                        continue
                    dependencies = [w, *dependencies]
                    changed = True
        # convert to list of modules
        return [self[d.name] for d in dependencies]

    def install_local(self, name: str, force: bool = False):
        module = self[name]
        tree = self._get_dependency_tree(module)
        for dependency in tree:
            if dependency.is_installed():
                if force:
                    click.secho(
                        f"Dependency {dependency.name} is installed, reinstalling.",
                        fg="green",
                    )
                else:
                    click.secho(
                        f"Dependency {dependency.name} is already installed.",
                        fg="green",
                    )
                    continue
            click.secho(
                f"Installing dependency {dependency.name} locally...", fg="blue"
            )
            dependency.install_local(force=force)
        print()
        click.secho(f"Installing module {module.name} locally.", fg="blue")
        module.install_local(force=force)

    def install_system(self, name: str, force: bool = False):
        module = self[name]
        tree = self._get_dependency_tree(module)
        for dependency in tree:
            if dependency.is_installed():
                print()
                if force:
                    click.secho(
                        f"Dependency {dependency.name} is installed, reinstalling.",
                        fg="green",
                    )
                else:
                    click.secho(
                        f"Dependency {dependency.name} is already installed.",
                        fg="green",
                    )
                    continue
            click.secho(
                f"Installing dependency {dependency.name} to system...", fg="blue"
            )
            dependency.install_system(force=force)
        print()
        click.secho(f"Installing module {module.name} to system...", fg="blue")
        module.install_system(force=force)
