#!/usr/bin/env bash

COLOR_BOLD_YELLOW="\033[1;33m"
COLOR_BOLD_BLUE="\033[1;34m"
COLOR_BOLD_MAGENTA="\033[1;35m"
COLOR_BOLD_CYAN="\033[1;36m"
COLOR_RESET="\033[m"

CONFIG=config/artful
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

recipe "name: sumo"
echo "platform: ubuntu:17.10"
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
sudo apt-get update && sudo apt-get dist-upgrade -y


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








###########################################################################

section ">>> latex"



sudo apt-get update && sudo apt-get install -y \
    pandoc \
    lmodern \
    texlive-generic-recommended \
    texlive-fonts-recommended \
    texlive-humanities \
    texlive-latex-extra \
    texlive-xetex \
    texinfo \
 && echo "latex debian packages installed"





sudo apt-get purge -y \
    texlive-latex-extra-doc \
    texlive-pictures-doc \
    texlive-latex-base-doc \
    texlive-latex-recommended-doc \
    texlive-humanities-doc \
 && echo "latex packages purged"

echo "post-install scripts"
cd /usr/share/texlive/texmf-dist
sudo wget http://mirrors.ctan.org/install/fonts/inconsolata.tds.zip
sudo unzip inconsolata.tds.zip
sudo rm inconsolata.tds.zip
echo "Map zi4.map" | sudo tee --append /usr/share/texlive/texmf-dist/web2c/updmap.cfg
sudo mktexlsr
sudo updmap-sys



###########################################################################

section ">>> rlang"



sudo apt-get update && sudo apt-get install -y \
    fonts-texgyre \
    libssl-dev \
    libxml2-dev \
    libcurl4-openssl-dev \
    libcairo2-dev \
    libxt-dev \
    libssh2-1-dev \
    r-base \
    r-base-dev \
    r-recommended \
 && echo "rlang debian packages installed"








###########################################################################

section ">>> rlang-packages"







sudo Rscript -e "install.packages(c('crayon', 'd3heatmap', 'data.table', 'dbplyr', 'devtools', 'DiagrammeR', 'docopt', 'DT', 'dtplyr', 'dygraphs', 'flexdashboard', 'forecast', 'formattable', 'ggalt', 'ggiraph', 'ggcorrplot', 'ggExtra', 'ggthemes', 'gmodels', 'highcharter', 'IRdisplay', 'janitor', 'leaflet', 'metricsgraphics', 'networkD3', 'openxlsx', 'pander', 'pbdZMQ', 'plotly', 'qcc', 'rbokeh', 'RColorBrewer', 'repr', 'rhandsontable', 'rmarkdown', 'rmdshower', 'rpivotTable', 'RPostgres', 'scales', 'shiny', 'shinydashboard', 'shinythemes', 'tidyverse', 'timevis', 'treemapify', 'visNetwork', 'xtable', 'zoo'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rstudio"



sudo apt-get update && sudo apt-get install -y \
    libjpeg62 \
    libgstreamer1.0-0 \
    libgstreamer-plugins-base1.0-0 \
 && echo "rstudio debian packages installed"






echo "post-install scripts"
RSTUDIO=rstudio-xenial-1.1.442-amd64.deb
wget https://download1.rstudio.org/$RSTUDIO
sudo dpkg -i $RSTUDIO
rm $RSTUDIO



###########################################################################

section ">>> docker"






DOCKER=get-docker.sh
curl -fsSL get.docker.com -o $DOCKER
sudo sh $DOCKER
sudo usermod -aG docker $USER
rm $DOCKER

echo "docker installed"





###########################################################################

section ">>> sublime-text"


echo "pre-install scripts"
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add
sudo apt-get install apt-transport-https
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list


sudo apt-get update && sudo apt-get install -y \
    sublime-text \
 && echo "sublime-text debian packages installed"








###########################################################################

section ">>> golang"






GOLANG=go1.9.2.linux-amd64.tar.gz
wget https://redirector.gvt1.com/edgedl/go/$GOLANG
sudo tar -C /usr/local -xzf $GOLANG
rm -rf $GOLANG

echo "golang installed"





###########################################################################

section ">>> rust-lang"






curl https://sh.rustup.rs -sSf | sh

echo "rust-lang installed"





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


