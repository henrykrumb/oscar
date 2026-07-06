# oscar

`oscar` is a project management utility for OpenSCAD.



[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/release/python-3140/)


Features:
* Semantic versioning of parts

Planned features:
* Auto-export 3D models (e.g. STL) upon save (optional)
* Packing and unpacking projects for distribution
* Auto-generate thumbnails
* Generate animations
* Explosion drawings
* Dimension drawings
* Last modified date as special variable
* Adding libraries through an index of common libs or links to git repo
* Make oscar-managed projects installable within other oscar projects


## Installation

Download and install [OpenSCAD](https://openscad.org/downloads.html) by following the instructions on the website.
On Debian-based systems (Debian, Ubuntu, Mint,...), it should be available from the official repos:

```bash
sudo apt install openscad
```

Install astral uv by following the official [instructions](https://docs.astral.sh/uv/getting-started/installation/) for your system.
If you run macOS, GNU/Linux or similar system, you can run:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Once uv is installed, run the following commands to install `oscar` in your user home:

```bash
git clone https://github.com/henrykrumb/oscar.git
cd oscar
uvx tool install .
```


## Getting Started

To create a new project titled *myproject*, call:

```bash
oscar new myproject
cd myproject
```

This will create a new project directory with the following structure:

```
myproject
├── build/
├── .gitignore
├── oscar.toml
└── src/
    ├── main.scad
    └── _parts.scad
```

`oscar.toml` is the main config file of the project. For a fresh project, it will contain the following information:

```toml
[project]
name = "myproject"
version = "0.1.0"
oscar = "0.1.0"

[project.variables]

[project.modules]
```

### Build

Running

```
oscar build
```

inside the project root directory will build all `*.scad` files in `src/` that do not start with an underscore, and save the resulting 3D models in `build/` under the same name as the source file.
Check out `oscar build --help` for a list of supported output file formats (can be passed with `-f` argument).
For our example project, `build/` will be populated like this:

```
myproject/build/
└── main.stl
```

Please note that no STL file was generated for `_parts.scad`, as it is considered an auxiliary module starting with an underscore.


### Edit

Inside the project directory, you can run the OpenSCAD GUI with project-specific variables included, by running:

```bash
oscar edit
```

In order to watch for changes and automatically build the STL on every save, pass the `-w` or `--watch` flag:

```bash
oscar edit -w
```




## Packing and Unpacking projects

```bash
oscar pack
```

```bash
oscar unpack MYPROJECT.zip
```




## Cleaning up

To remove all artifacts generated through `oscar build`, run:

```bash
oscar clean
```


## Special Variables

If you're designing a part and want to keep track of its version, you can directly access it from OpenSCAD (if opened through `oscar edit`).
For instance, this piece of code would show the version and project name in a 3D shape:

```openscad
linear_extrude(1) {
    text(project_version);
    translate([0, 100, 0])
    text(project_name);
}
```

You can also create custom variables in `oscar.toml` like so:

```toml
[project]
name = "myproject"
version = "0.1.0"
oscar = "0.1.0"

[project.variables]
myvar = 42

[project.modules]

```

which can then be accessed in your OpenSCAD code directly:

```openscad
cube([myvar, myvar, myvar]); // will create a 42x42x42 cube
```


## Installing third-party modules

Coming soon.

## Semantic versioning

Your oscar project is versioned according to the semantic versioning syntax (simplified to major.minor.patch for now).
If you're planning to increment the version of your oscar project, you could either edit `oscar.toml` or call:
 `oscar bump patch`, `oscar bump minor` or `oscar bump major` respectively.
 For now, these commands should have no notable side effects apart from making an edit to `oscar.toml` (while validating the project layout and version string).

## Config overrides

It is possible to specify a scad-file-specific configuration by prepending a shebang-line
at the start of a file (can be prefixed by empty lines or whitespace).
For instance, if your project mainly exports STL files, but a single file is a 2D object that is supposed to be
exported to SVG, you could prepend the following shebang line:

```OpenSCAD
// export-format=svg
circle(r=10);
```
