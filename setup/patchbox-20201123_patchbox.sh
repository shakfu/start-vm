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

recipe "name: audiomachine"
echo "platform: patchbox-20201123"
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
    sqlite3 \
    litecli \
    grin \
    isort \
    pylint \
    black \
 && echo "py_modules python packages installed"







###########################################################################

section ">>> gui"



sudo apt-get update && sudo apt-get install -y \
    xorg \
    xserver-xorg-input-all \
    fonts-dejavu \
    awesome \
    xfce4-terminal \
    lxappearance \
    gtk2-engines \
    conky \
    scite \
    gtkorphan \
    fslint \
    bleachbit \
 && echo "gui debian packages installed"








###########################################################################

section ">>> powerline-fonts"






git clone https://github.com/powerline/fonts.git --depth=1
cd fonts
./install.sh
cd ..
rm -rf fonts

echo "powerline-fonts installed"



echo "post-install scripts"
sudo apt-get autoremove
sudo apt-get autoclean
sudo apt-get clean



###########################################################################

section ">>> audio"



sudo apt-get update && sudo apt-get install -y \
    sox \
    None \
 && echo "audio debian packages installed"








###########################################################################

section ">>> py_audio"




sudo -H pip3 install \
    aubio \
    librosa \
    mido \
    mingus \
    miniaudio \
    music21 \
    pippi \
    PyAudio \
    pydub \
    pyliblo \
    pyo \
    pyrubberband \
    PySoundFile \
    python-osc \
    python-rtmidi \
    PyTuning \
    sox \
    soxbindings \
 && echo "py_audio python packages installed"







###########################################################################

section ">>> puredata"



sudo apt-get update && sudo apt-get install -y \
    puredata \
    puredata-dev \
    pd-3dp \
    pd-ableton-link \
    pd-ambix \
    pd-arraysize \
    pd-aubio \
    pd-autopreset \
    pd-bassemu \
    pd-beatpipe \
    pd-blokas \
    pd-boids \
    pd-bsaylor \
    pd-chaos \
    pd-cmos \
    pd-comport \
    pd-creb \
    pd-csound \
    pd-cxc \
    pd-cyclone \
    pd-deken \
    pd-deken-apt \
    pd-earplug \
    pd-ekext \
    pd-ext13 \
    pd-extendedview \
    pd-fftease \
    pd-flext-dev \
    pd-flext-doc \
    pd-flite \
    pd-freeverb \
    pd-ggee \
    pd-gil \
    pd-hcs \
    pd-hexloader \
    pd-hid \
    pd-iem \
    pd-iemambi \
    pd-iemguts \
    pd-iemlib \
    pd-iemmatrix \
    pd-iemnet \
    pd-iemtab \
    pd-iemutils \
    pd-jmmmp \
    pd-jsusfx \
    pd-kollabs \
    pd-lib-builder \
    pd-libdir \
    pd-list-abs \
    pd-log \
    pd-lua \
    pd-lyonpotpourri \
    pd-mapping \
    pd-markex \
    pd-maxlib \
    pd-mediasettings \
    pd-mjlib \
    pd-moonlib \
    pd-motex \
    pd-mrpeach \
    pd-mrpeach-net \
    pd-nusmuk \
    pd-osc \
    pd-pan \
    pd-pddp \
    pd-pdogg \
    pd-pdp \
    pd-pdstring \
    pd-pduino \
    pd-plugin \
    pd-pmpd \
    pd-pool \
    pd-puremapping \
    pd-purepd \
    pd-purest-json \
    pd-py \
    pd-readanysf \
    pd-rtclib \
    pd-sigpack \
    pd-slip \
    pd-smlib \
    pd-syslog \
    pd-tclpd \
    pd-testtools \
    pd-unauthorized \
    pd-upp \
    pd-vbap \
    pd-wiimote \
    pd-windowing \
    pd-xbee \
    pd-xsample \
    pd-zexy \
 && echo "puredata debian packages installed"







