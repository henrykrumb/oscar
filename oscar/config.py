from pathlib import Path

USER_CONFIG_PATH = Path.home() / ".oscar"
USER_CONFIG_PATH.mkdir(exist_ok=True)

MODULE_INDEX_PATH = USER_CONFIG_PATH / "index.toml"


DEFAULT_MODULE_INDEX = """\
[modules]
[modules.BOLTS]
clone = "https://github.com/boltsparts/BOLTS_archive"
license = [ "LGPL-2.1-or-later", "GPL-3.0-only" ]

[modules.BOSL]
download = "https://github.com/revarbat/BOSL/archive/refs/tags/v1.0.3.zip"
license = "BSD-2-Clause"

[modules.BOSL2]
download = "https://github.com/BelfrySCAD/BOSL2/archive/refs/heads/master.zip"
license = "BSD-2-Clause"

[modules.constructive]
clone = "https://github.com/solidboredom/constructive"
license = "GPL-2.0"

[modules.dotSCAD]
download = "https://github.com/JustinSDK/dotSCAD/archive/refs/tags/v3.3.zip"

[modules.FunctionalOpenSCAD]
clone = "https://github.com/thehans/FunctionalOpenSCAD"

[modules.list-comprehension-demos]
clone = "https://github.com/openscad/list-comprehension-demos"

[modules.NopSCADlib]
clone = "https://github.com/nophead/NopSCADlib"

[modules.scad-utils]
clone = "https://github.com/openscad/scad-utils"

[modules.StoneAgeLib]
clone = "https://github.com/Stone-Age-Sculptor/StoneAgeLib"
license = "CC0-1.0"

[modules.thread-profile]
download = "https://github.com/MisterHW/IoP-satellite/blob/master/OpenSCAD%20bottle%20threads/thread_profile.scad"

[modules.threadlib]
wants = [ "scad-utils", "list-comprehension-demos", "thread-profile" ]
clone = "https://github.com/adrianschlatter/threadlib"

[modules.UBscad]
name = "UB.scad"
download = "https://raw.githubusercontent.com/UBaer21/UB.scad/main/libraries/ub.scad"
"""


if not MODULE_INDEX_PATH.exists():
    MODULE_INDEX_PATH.write_text(DEFAULT_MODULE_INDEX)
