from pathlib import Path

USER_CONFIG_PATH = Path.home() / ".oscar"
USER_CONFIG_PATH.mkdir(exist_ok=True)

MODULE_INDEX_PATH = USER_CONFIG_PATH / "index.toml"


DEFAULT_MODULE_INDEX = """\
[modules]
[modules.BOSL]
download = "https://github.com/revarbat/BOSL/archive/refs/tags/v1.0.3.zip"
license = "BSD-2-Clause"

[modules.BOSL2]
download = "https://github.com/BelfrySCAD/BOSL2/archive/refs/heads/master.zip"
license = "BSD-2-Clause"

[modules.dotSCAD]
download = 

[modules.thread-profile]
download = "https://github.com/MisterHW/IoP-satellite/blob/master/OpenSCAD%20bottle%20threads/thread_profile.scad"

[modules.list-comprehension-demos]
clone = "https://github.com/openscad/list-comprehension-demos"

[modules.scad-utils]
clone = "https://github.com/openscad/scad-utils"

[modules.threadlib]
wants = [ "scad-utils", "list-comprehension-demos", "thread-profile" ]
clone = "https://github.com/adrianschlatter/threadlib"
"""


if not MODULE_INDEX_PATH.exists():
    MODULE_INDEX_PATH.write_text(DEFAULT_MODULE_INDEX)
