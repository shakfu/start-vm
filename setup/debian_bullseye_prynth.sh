#!/usr/bin/env bash
COLOR_BOLD_YELLOW="\033[1;33m"
COLOR_BOLD_BLUE="\033[1;34m"
COLOR_BOLD_MAGENTA="\033[1;35m"
COLOR_BOLD_CYAN="\033[1;36m"
COLOR_RESET="\033[m"
CONFIG=config/console
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
recipe "name: prynth"
echo "platform: debian:bullseye"
echo
section ">>> installing default dotfiles"
install_default .fonts
install_default bin
install_default .vimrc-heavy
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
install_config .keep
###########################################################################
section ">>> core"
echo "pre-install scripts"
sudo apt update && sudo apt dist-upgrade -y
sudo apt-get update && sudo apt-get install -y \
    git \
    build-essential \
    cmake \
    ncdu \
    htop \
    neovim \
    tig \
    bmon \
    pv \
    rpl \
    unzip \
    p7zip-full \
 && echo "core debian packages installed"
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
    grin \
    isort \
    ranger-fm \
 && echo "py_modules python packages installed"
###########################################################################
section ">>> libraries"
sudo apt-get update && sudo apt-get install -y \
    nodejs \
    liblo7 \
    wiringpi \
 && echo "libraries debian packages installed"
###########################################################################
section ">>> infrastructure"
sudo apt-get update && sudo apt-get install -y \
    libsamplerate0-dev \
    libsndfile1-dev \
    libasound2-dev \
 && echo "infrastructure debian packages installed"
###########################################################################
section ">>> jack"
git clone git://github.com/jackaudio/jack2 --depth 1
cd jack2
./waf configure --alsa
./waf build
sudo ./waf install
sudo ldconfig
cd .. && rm -rf jack2
echo "jack installed"
echo "post-install scripts"
sudo sh -c "echo @audio - memlock 256000 >> /etc/security/limits.conf"
sudo sh -c "echo @audio - rtprio 75 >> /etc/security/limits.conf"
###########################################################################
section ">>> supercollider"
git clone --recurse-submodules https://github.com/supercollider/supercollider.git
cd supercollider
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DSUPERNOVA=OFF -DSC_ED=OFF -DSC_EL=OFF -DSC_VIM=ON -DNATIVE=ON -DSC_IDE=OFF -DNO_X11=ON -DSC_QT=OFF ..
sudo cmake --build . --config Release --target install
sudo ldconfig
echo "supercollider installed"
###########################################################################
section ">>> prynth"
cd ~
git clone https://github.com/prynth/prynth.git
echo "prynth installed"
echo "post-install scripts"
gcc -o /home/pi/prynth/pbridge/pbridge /home/pi/prynth/pbridge/src/pbridge.c -lwiringPi -llo