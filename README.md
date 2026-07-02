# oscar

`oscar` is a project management utility for OpenSCAD.



[![Python 3.10](https://img.shields.io/badge/python-3.10-blue.svg)](https://www.python.org/downloads/release/python-3100/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Python 3.14](https://img.shields.io/badge/python-3.14-blue.svg)](https://www.python.org/downloads/release/python-3140/)


Features:
* Configure 
* Auto-export 3D models (e.g. STL) upon save (optional)

Planned features:
* Auto-generate thumbnails
* Generate animations
* Explosion drawings
* Dimension drawings


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
├── build
├── oscar.toml
└── src
    ├── main.scad
    └── _parts.scad
```

`oscar.toml` is the main config file of the project. For a fresh project, it will contain the following information:

```toml
[project]
name = "myproject"
version = "0.1.0"
oscar = "0.1.0"
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

```bash
oscar clean
```


## Special Variables