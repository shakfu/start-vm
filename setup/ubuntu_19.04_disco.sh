#!/usr/bin/env bash

COLOR_BOLD_YELLOW="\033[1;33m"
COLOR_BOLD_BLUE="\033[1;34m"
COLOR_BOLD_MAGENTA="\033[1;35m"
COLOR_BOLD_CYAN="\033[1;36m"
COLOR_RESET="\033[m"

CONFIG=config/disco
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

recipe "name: disco"
echo "platform: ubuntu:19.04"
echo

section ">>> installing default dotfiles"
install_default .fonts
install_default bin
install_default .bashrc
install_default .SciTEUser.properties
install_default .xinitrc
install_default .gtkrc-2.0
install_default .vimrc
install_default .ghci
install_default src

section ">>> installing .config folders"
if [ ! -d "$CONFIG_DST" ]; then
    mkdir -p $CONFIG_DST
fi
install_config conky
install_config gtk-3.0
install_config xfce4
install_config i3status
install_config i3
install_config awesome


###########################################################################

section ">>> core"


echo "pre-install scripts"
sudo apt update && sudo apt dist-upgrade -y


sudo apt-get update && sudo apt-get install -y \
    build-essential \
    cmake \
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
# Reset font cache on Linux
if command -v fc-cache @>/dev/null ; then
    echo "Resetting font cache"
    fc-cache -f $HOME/.fonts
fi



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
    psycopg2-binary \
    pgcli \
    grin \
    isort \
    pylint \
    radon \
    autopep8 \
    glances \
 && echo "py_modules python packages installed"







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







