from pathlib import Path

USER_CONFIG_PATH = Path.home() / ".oscar"
USER_CONFIG_PATH.mkdir(exist_ok=True)

MODULE_INDEX_PATH = USER_CONFIG_PATH / "index.toml"


DEFAULT_MODULE_INDEX = """\
[modules]
[modules.BOSL2]
download = "https://github.com/BelfrySCAD/BOSL2/archive/refs/heads/master.zip"
"""


if not MODULE_INDEX_PATH.exists():
    MODULE_INDEX_PATH.write_text(DEFAULT_MODULE_INDEX)
