# start-vm

Generates bash setup files from yaml `recipe` files for 1-step setup of linux-based virtual or physical machines.

Do **NOT** use on a pre-existing installation as this program may well over-write your files. You have been warned!




## Basic usage: Installation

Install a fresh ubuntu server 16.04 LTS distro on a virtual or physical machine engine and then:

```
$ git clone https://github.com/shakfu/start-vm

$ cd start-vm

$ ./setup/ubuntu_16.04_base.sh
```

## Basic usage: Generation

To generate a `setup/<platform-recipt>.sh` file from a `recipes/<recipe>.yml` file:

```
$ install.py --bashfile recipes/<recipe>.yml
```

The generated bash recipe files are created in the `setup` folder

**IMPORTANT NOTE**: As of the current implementation *everything* in `default` is copied into `$HOME` and *everything* in `config` is copied into `$HOME/.config`.

A minimal ubuntu 16.04 LTS `base.yml` is implemented. Forks and and pull requests for other variations are of course wellcome.

Future plans include the generation of Dockerfiles from recipe.yml files.

## Creating new recipes

Recipe files are yaml files with a certain structure. The easiest way to learn is to just customize the included `base.yml` example:

```yaml
name: base
platform: ubuntu:16.04
sections:
    - name: core
      type: debian_packages
      pre_install: |
        sudo apt-get update && sudo apt-get dist-upgrade -y
      install:
        - build-essential
        - ncdu
        - htop
        - vim
        - exuberant-ctags
        - tig
        - ranger
        - bmon
        - pv
        - rpl
        - unzip
        - p7zip-full
        - open-vm-tools
        - open-vm-tools-desktop
      purge:
        - snapd
      post_install: |
        mkdir -p ~/.host-shared

    - name: database
      type: debian_packages
      pre_install: |
        declare DEB="deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main"
        echo "$DEB" | sudo tee --append /etc/apt/sources.list.d/pgdg.list
        wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | sudo apt-key add -
        sudo apt-get update
      install:
        - libpq-dev
        - postgresql-client-9.6
        - postgresql-9.6
        - postgresql-contrib-9.6
        - postgresql-plpython3-9.6
        - postgresql-9.6-pllua
        - luajit
        - postgresql-9.6-pgtap
        - pgtap
      post_install: |
        sudo -u postgres createuser -s sa
        sudo -u postgres createdb sa

    - name: python
      type: debian_packages
      install:
        - python3-dev
        - python3-setuptools
        - python3-pip

    - name: py_modules
      type: python_packages
      install:
          - wheel
          - virtualenv
          - ipython
          - cython
          - psycopg2
          - pgcli
          - grin
          - isort
          - pylint
          - radon
          - autopep8
          - glances

    - name: gui
      type: debian_packages
      install:
          - xorg
          - fonts-dejavu
          - gnome-icon-theme
          - awesome
          - i3
          - roxterm
          - lxappearance
          - gtk2-engines
          - conky
          - scite
          - gtkorphan
          - fslint
          - bleachbit
```
