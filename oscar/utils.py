from pathlib import Path
from typing import Dict

from .constants import SUPPORTED_EXPORT_FORMATS

_CONFIG_KEYS = ("export-format",)


def parse_scad_shebang(scad_path: Path) -> Dict[str, str]:
    """
    Parse the first single-line comment inside an OpenSCAD file, which may
    contain a config string that overrides command line arguments.

    This is particularly useful in cases where certain files in a project
    should be exported to a certain format, e.g. to SVG in a project that
    is otherwise dominated by 3D models.

    This function parses the first line with a non-whitespace character and
    checks for a single-line comment (starting with //). Whatever comes
    afterwards should have the format:

    ```OpenSCAD
    // key1=value1; key2=value2
    ```

    Where currently, only `export-format` is supported as a key identifier,
    providing an override for the export format defined in CLI.
    """
    text = scad_path.read_text()
    lines = [L.strip() for L in text.splitlines() if len(L.strip()) > 0]
    if len(lines) == 0:
        return {}
    firstline = lines[0]
    if not firstline.startswith("//"):
        return {}
    config_string = firstline[2:]
    config_string = config_string.strip()
    pairs = [pair.split("=") for pair in config_string.split(";")]
    assert all([len(pair) == 2 for pair in pairs])
    config = {p[0].strip(): p[1].strip() for p in pairs if p[0].strip() in _CONFIG_KEYS}
    assert config.get("export-format") in (None, *SUPPORTED_EXPORT_FORMATS)
    return config
