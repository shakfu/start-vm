#!/usr/bin/env bash

COLOR_BOLD_YELLOW="\033[1;33m"
COLOR_BOLD_BLUE="\033[1;34m"
COLOR_BOLD_MAGENTA="\033[1;35m"
COLOR_BOLD_CYAN="\033[1;36m"
COLOR_RESET="\033[m"

CONFIG=config/base
DEFAULT=default
CONFIG_DST=$HOME/.config
BIN=$HOME/bin

function recipe {
    echo
    echo -e $COLOR_BOLD_MAGENTA$1 $COLOR_RESET
    echo "=========================================================="
}

function section {
    echo
    echo -e $COLOR_BOLD_CYAN$1 $COLOR_RESET
    echo "----------------------------------------------------------"
}

function install_default {
    echo "installing $1"
    cp -rf $DEFAULT/$1 $HOME/
}

function install_config {
    echo "installing $1"
    cp -rf $CONFIG/$1 $CONFIG_DST/
}

recipe "name: base"
echo "platform: ubuntu:17.10"
echo

section ">>> installing default dotfiles"
install_default .vimrc
install_default bin
install_default .SciTEUser.properties
install_default .fonts
install_default .bashrc
install_default src
install_default .xinitrc
install_default .ghci

section ">>> installing .config folders"
if [ ! -d "$CONFIG_DST" ]; then
    mkdir -p $CONFIG_DST
fi
install_config gtk-3.0
install_config roxterm.sourceforge.net
install_config i3
install_config i3status
install_config awesome
install_config xfce4
install_config conky


###########################################################################

section ">>> core"


echo "pre-install scripts"
sudo apt-get update && sudo apt-get dist-upgrade -y


sudo apt-get update && sudo apt-get install -y \
    build-essential \
    ncdu \
    htop \
    vim \
    exuberant-ctags \
    tig \
    ranger \
    bmon \
    pv \
    rpl \
    unzip \
    p7zip-full \
    open-vm-tools \
 && echo "core debian packages installed"




sudo apt-get purge -y \
    snapd \
 && echo "core packages purged"

echo "post-install scripts"
mkdir -p ~/.host-shared



###########################################################################

section ">>> python"



sudo apt-get update && sudo apt-get install -y \
    python3-dev \
    python3-setuptools \
    python3-pip \
 && echo "python debian packages installed"







###########################################################################

section ">>> py_modules"




sudo -H pip3 install \
    wheel \
    virtualenv \
    ipython \
    cython \
    psycopg2 \
    pgcli \
    grin \
    isort \
    pylint \
    radon \
    autopep8 \
    glances \
 && echo "py_modules python packages installed"






###########################################################################

section ">>> database"



sudo apt-get update && sudo apt-get install -y \
    libpq-dev \
    postgresql-client-9.6 \
    postgresql-9.6 \
    postgresql-contrib-9.6 \
    postgresql-plpython3-9.6 \
    postgresql-9.6-pllua \
    luajit \
    postgresql-9.6-pgtap \
    pgtap \
 && echo "database debian packages installed"





echo "post-install scripts"
sudo -u postgres createuser -s $USER
sudo -u postgres createdb $USER



###########################################################################

section ">>> gui"



sudo apt-get update && sudo apt-get install -y \
    xorg \
    xserver-xorg-input-all \
    open-vm-tools-desktop \
    fonts-dejavu \
    gnome-icon-theme \
    awesome \
    i3 \
    xfce4-terminal \
    lxappearance \
    gtk2-engines \
    conky \
    scite \
    gtkorphan \
    fslint \
    bleachbit \
 && echo "gui debian packages installed"






