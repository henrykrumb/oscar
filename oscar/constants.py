from typing import Literal

"""
List of legal OpenSCAD export formats
"""
SUPPORTED_EXPORT_FORMATS = [
    "stl",
    "csg",
    "dxf",
    "amf",
    "off",
    "svg",
    "png",
    "pdf",
    "echo",
    "ast",
    "term",
    "nef3",
    "nefdbg",
]

"""
Type hint for function arguments (or variables) that represent a legal OpenSCAD export format
"""
ExportFormatType = Literal[
    "stl",
    "csg",
    "dxf",
    "amf",
    "off",
    "svg",
    "png",
    "pdf",
    "echo",
    "ast",
    "term",
    "nef3",
    "nefdbg",
]
