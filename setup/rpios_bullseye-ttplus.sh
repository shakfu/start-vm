#!/usr/bin/env bash
COLOR_BOLD_YELLOW="\033[1;33m"
COLOR_BOLD_BLUE="\033[1;34m"
COLOR_BOLD_MAGENTA="\033[1;35m"
COLOR_BOLD_CYAN="\033[1;36m"
COLOR_RESET="\033[m"
CONFIG=config/bullseye
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
recipe "name: ttplus"
echo "platform: rpios"
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
install_config awesome
###########################################################################
section ">>> core_dev"
echo "pre-install scripts"
sudo apt update && sudo apt dist-upgrade -y
sudo apt-get update && sudo apt-get install -y \
    git \
    build-essential \
    cmake \
    autoconf \
    libtool \
    automake \
    bison \
    flex \
    swig \
    indent \
    upx-ucl \
    vim-nox \
    exuberant-ctags \
    ncdu \
    htop \
    rpl \
    tmux \
    pv \
    unzip \
    p7zip-full \
    tig \
    ranger \
    bmon \
    sqlite3 \
    nodejs \
 && echo "core_dev debian packages installed"
###########################################################################
section ">>> core_libs"
sudo apt-get update && sudo apt-get install -y \
    libavahi-client-dev \
    libreadline-dev \
    libfftw3-dev \
    libudev-dev \
    libncurses5-dev \
    libssl-dev \
    libgc-dev \
    libluajit-5.1-dev \
 && echo "core_libs debian packages installed"
###########################################################################
section ">>> core_audio_libs"
sudo apt-get update && sudo apt-get install -y \
    sox \
    ffmpeg \
    lame \
    flac \
    libsox-dev \
    libsndfile1-dev \
    libasound2-dev \
    libportaudio-dev \
    libportmidi-dev \
    librtaudio-dev \
    librtmidi-dev \
    libsamplerate0-dev \
    liblo-dev \
    libcsnd6-6.0v5 \
 && echo "core_audio_libs debian packages installed"
###########################################################################
section ">>> jack"
git clone https://github.com/jackaudio/jack2 --depth 1
cd jack2
./waf configure --alsa --libdir=/usr/lib/arm-linux-gnueabihf/
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
cd ..
echo "supercollider installed"
echo "post-install scripts"
# setup jack
# `-dhw:0` is the internal soundcard. Use `-dhw:1` for USB soundcards. `aplay -l` will list available devices.
echo /usr/local/bin/jackd -P75 -p16 -dalsa -dhw:0 -r44100 -p1024 -n3 > ~/.jackdrc
###########################################################################
section ">>> sc3-plugins"
git clone --recursive https://github.com/supercollider/sc3-plugins.git
cd sc3-plugins
mkdir build && cd build
# for both scsynth and supernova plugins; set -DSUPERNOVA=OFF to build only scsynth plugins
cmake -DSC_PATH=../../supercollider -DCMAKE_BUILD_TYPE=Release -DSUPERNOVA=OFF ..
cmake --build . --config Release
sudo cmake --build . --config Release --target install
sudo ldconfig
echo "sc3-plugins installed"
###########################################################################
section ">>> puredata"
sudo apt-get update && sudo apt-get install -y \
    puredata \
    puredata-dev \
    pd-3dp \
    pd-ableton-link \
    pd-ambix \
    pd-arraysize \
    pd-autopreset \
    pd-bassemu \
    pd-beatpipe \
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
###########################################################################
section ">>> audio_extras"
sudo apt-get update && sudo apt-get install -y \
    csound \
    faust \
    fluidsynth \
    fluid-soundfont-gs \
    timidity \
    pmidi \
    midish \
 && echo "audio_extras debian packages installed"
echo "post-install scripts"
git clone https://github.com/hundredrabbits/Orca-c.git
cd Orca-c
make
sudo cp build/orca /usr/local/bin/orca
###########################################################################
section ">>> audio_extras_2"
sudo apt-get update && sudo apt-get install -y \
    ableton-link-utils \
    flac \
    paulstretch \
 && echo "audio_extras_2 debian packages installed"
###########################################################################
section ">>> python"
sudo apt-get update && sudo apt-get install -y \
    python3-dev \
    python3-setuptools \
    python3-pip \
    python3-numpy \
 && echo "python debian packages installed"
###########################################################################
section ">>> py_modules"
sudo -H pip3 install \
    wheel \
    virtualenv \
    ipython \
    cython \
    litecli \
    grin \
    isort \
    pylint \
    pytest \
    black \
 && echo "py_modules python packages installed"
###########################################################################
section ">>> py_audio1"
sudo apt-get update && sudo apt-get install -y \
    python3-alsaaudio \
    python3-aubio \
    python3-csound \
    python3-ecasound \
    python3-jack-client \
    python3-liblo \
    python3-llvmlite \
    python3-midiutil \
    python3-mido \
    python3-pyknon \
    python3-pyo \
    python3-pyaudio \
    python3-rtmidi \
 && echo "py_audio1 debian packages installed"
###########################################################################
section ">>> py_audio2"
sudo -H pip3 install \
    mingus \
    miniaudio \
    music21 \
    pydub \
    pyrubberband \
    PySoundFile \
    python-osc \
    PyTuning \
    sox \
    soxbindings \
 && echo "py_audio2 python packages installed"
###########################################################################
section ">>> haskell_packages"
sudo apt-get update && sudo apt-get install -y \
    haskell-platform \
 && echo "haskell_packages debian packages installed"
echo "post-install scripts"
cabal update
cabal install --lib tidal
cabal install --lib csound-expression
cd ~
cat > install_superdirt.scd << EOF
Quarks.checkForUpdates({Quarks.install("SuperDirt", "v1.7.3"); thisProcess.recompile()});
EOF
echo "reboot and then run 'sclang superdirt.scd'"