# start-vm: 1 step setups for fresh machines

Generates bash scripts from yaml `recipe` files for 1-step setup of linux-based virtual or physical machines.

Do **NOT** use on a pre-existing installation as this program may well over-write your files. You have been warned!

## Features

- Generation of bash setup scripts in one of two modes:

    1. Auto-mode: without asking for permission (default)

    2. Conditional mode: asks for permission to install at each step.

- Auto-run script after generation

## Basic Usage

### Clone and Install

Install a fresh ubuntu server 20.04 LTS distro on a virtual or physical machine engine and then:

```bash
git clone https://github.com/shakfu/start-vm

cd start-vm

./setup/ubuntu_20.04_focal.sh
```

### Clone, Generate and Install

To generate a `setup/<platform-recipt>.sh` file from a `recipes/<recipe>.yml` file:

```bash
start_vm.py --bashfile --conditional recipes/<recipe>.yml
```

The generated bash recipe files are created in the `setup` folder

**IMPORTANT NOTE**: As of the current implementation *everything* in `default` is copied into `$HOME`.

What is copied out of config is a function of which recipe is used such that *everything* in `config/<recipe>` is copied into `$HOME/.config`.

A minimal ubuntu 16.04 LTS `base.yml` is implemented. Forks and pull requests for other variations are of course wellcome.

Future plans include the generation of Dockerfiles from `<recipe>.yml` files.

## Command-line Usage

```text
usage: start_vm.py [-h] [--docker] [--bash] [--conditional] [--run] [--strip]
                   [--executable]
                   recipe [recipe ...]

Install Packages

positional arguments:
  recipe             recipes to install

optional arguments:
  -h, --help         show this help message and exit
  --docker, -d       generate dockerfile
  --bash, -b         generate bash file
  --conditional, -c  add conditional steps
  --run, -r          run bash file
  --strip, -s        strip empty lines
  --executable, -e   make setup file executable
```

## Creating new recipes

Recipe files are yaml files with a certain structure. The easiest way to learn is to just customize the included `base.yml` example:

```yaml

name: rlang
config: disco
platform: ubuntu:20.04
sections:
    - name: core
      type: debian_packages
      pre_install: |
        sudo apt update && sudo apt dist-upgrade -y
      install:
        - build-essential
        - cmake
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
      purge:
        - snapd
      post_install: |
        mkdir -p ~/.host-shared
        # Reset font cache on Linux
        if command -v fc-cache @>/dev/null ; then
            echo "Resetting font cache"
            fc-cache -f $HOME/.fonts
        fi

    - name: java
      type: debian_packages
      install:
        - default-jdk

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
        - litecli
        - grin
        - isort
        - pylint
        - radon
        - autopep8
        - glances
        - black
        - radian

    - name: database
      type: debian_packages
      install:
        - libpq-dev
        - postgresql-client-12
        - postgresql-12
        - postgresql-contrib
        - postgresql-plpython3-12
        - postgresql-12-pllua
        - luajit
        - postgresql-12-pgtap
        - pgtap
      post_install: |
        sudo -u postgres createuser -s $USER
        sudo -u postgres createdb $USER

    - name: gui
      type: debian_packages
      install:
        - xorg
        - xserver-xorg-input-all
        - open-vm-tools-desktop
        - fonts-dejavu
        - gnome-icon-theme
        - awesome
        - i3
        - xfce4-terminal
        - lxappearance
        - gtk2-engines
        - conky
        - scite
        - gtkorphan
        - fslint
        - bleachbit

    - name: latex
      type: debian_packages
      install:
        - pandoc
        - lmodern
        - texinfo

    - name: rlang-debian
      type: debian_packages
      install:
        - fonts-texgyre
        - libssl-dev
        - libxml2-dev
        - libcurl4-openssl-dev
        - libcairo2-dev
        - libxt-dev
        - libssh2-1-dev
        - r-base
        - r-base-dev
        - r-recommended

    - name: rlang-latex
      type: rlang_packages
      install:
        - tinytex
      post_install: |
        Rscript -e "tinytex::install_tinytex()"

    - name: rlang-core
      type: rlang_packages
      install:
        - tidyverse
        - rmarkdown
        - docopt

    - name: rstudio
      type: debian_packages
      install:
          - libjpeg62
          - libgstreamer1.0-0
          - libgstreamer-plugins-base1.0-0
      post_install: |
        RSTUDIO_VER=1.4.1717
        RSTUDIO=rstudio-${RSTUDIO_VER}-amd64.deb
        wget https://download1.rstudio.org/desktop/bionic/amd64/$RSTUDIO
        sudo dpkg -i $RSTUDIO
        rm $RSTUDIO

    - name: sublime-text
      type: debian_packages
      pre_install: |
        wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add
        sudo apt-get install apt-transport-https
        echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
      install:
          - sublime-text

    - name: powerline-fonts
      type: bash
      install: |
        git clone https://github.com/powerline/fonts.git --depth=1
        cd fonts
        ./install.sh
        cd ..
        rm -rf fonts
      post_install: |
        sudo apt-get autoremove
        sudo apt-get autoclean
        sudo apt-get clean
``

## Current Implementations

- ubuntu 16.04 LTS
- ubuntu 17.10
- ubuntu 17.10 sumo edition
- ubuntu 19.04
- ubuntu 19.04 rlang edition
- ubuntu 20.04 LTS
