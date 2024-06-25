# start-vm: single-step setups for fresh machines

Generates bash scripts and dockerfiles from yaml `recipe` files to provide sigle-step setups of virtual or physical machines.

Do **NOT** use on a pre-existing installation as this program may well over-write your files. You have been warned!

## Features

- Setup specifications are captured in a yaml `recipe` file.

- Generation of shell setup scripts derived from the `recipe` file in one of two modes:

    1. Auto-mode: without asking for permission (default)

    2. Conditional mode: asks for permission to install at each step.

- Generation of Dockerfiles derived from the `recipe` file

- Many example recipes are provided in the projects with corresponding bash setup files.

## Basic Usage Patterns

### Clone and Install

For example, one can install a fresh ubuntu server 24.04 LTS distro on a virtual or physical machine engine and then:

```bash
git clone https://github.com/shakfu/start-vm

cd start-vm

./setup/linx_ubuntu_22.04_base.sh
```

This is the most common usage, clone start-vm and run one of its pre-generated and saved bash `setup_*` scripts. No python code is run or requirements installed.

### Clone, Generate and Install

For this case, `start_vm`'s requirements (`Jinja2` and `PyYAML`) should be installed:

```bash

pip install -r requirements.txt

```

To generate a `setup/<platform-recipt>.sh` file from a `recipes/<recipe>.yml` file:

```bash
start_vm.py --shell --conditional recipes/<recipe>.yml
```

The generated shell setup files are created in the `setup` folder

**IMPORTANT NOTE**: As of the current implementation *everything* in `default` is copied into `$HOME`.

What is copied out of config is a function of which recipe is used such that *everything* in `config/<recipe>` is copied into `$HOME/.config`.

A minimal ubuntu 24.04 LTS `base.yml` is implemented. Forks and pull requests for other variations are of course wellcome.

## Command-line Usage

```text
usage: start_vm.py [-h] [-d] [-b] [-c] [-f] [-r] [-s] [-e] [--section SECTION]
                   recipe [recipe ...]

Install Packages

positional arguments:
  recipe             recipes to install

options:
  -h, --help         show this help message and exit
  -d, --docker       generate dockerfile
  -b, --shell        generate shell file
  -c, --conditional  add conditional steps
  -f, --format       format using shfmt
  -r, --run          run shell file
  -s, --strip        strip empty lines
  -e, --executable   make setup file executable
  --section SECTION  run section
```

## The Model

```yaml
recipe:
  name: str
  config: str
  platform: str
  os: str
  version: str
  release: str
  inherits: Optional[str, list[str]]
  sections: list[section]
```

A `section` provides all the details for the installation and setup of a group of related installation targets which could be debian or ubuntu package, python modules, R packages or an application or library that is downloaded, configured and compiled from source.

It has the following structure:

```yaml
section:
  name: str
  type: str
  pre_install: Optional[str]
  install: list[str]
  purge: Optional[list[str]]
  post_install: Optional[str]
```

The optional `inherits` field provides for inheriting sections from multiple parent recipes.

The section inheritance algorithm is basic:

```python
child_section_names = [section['name'] for section in child_recipe['sections']]
for parent in parent_recipes:
    for section in parent['sections']:
      if section['name'] in child_section_names:
          continue
      child_recipe['sections'].append(section)
```

This is useful when one wants to have derivative recipes from a well specified and tested base recipe.

Note that configuration inheritance has not been implemented, so one has to be careful when using the inheritance feature and only inherit the a similarly configured base recipe.

## Creating new recipes

Recipe files are yaml files with a certain structure. The easiest way to learn is look at the provided recipes in this project. You can then pick a recipe and just customize it or or create a new recipe and inherit from a pre-existing one as above.

## TODO

- [ ] add powershell template for windows and windows pkg manager support

- [ ] add parameters which can be interpolated initially at the yaml level
