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

recipe "name: rlang"
echo "platform: ubuntu:19.10"
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


sudo apt update && sudo apt install -y \
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



echo "post-install scripts"
# Reset font cache on Linux
if command -v fc-cache @>/dev/null ; then
    echo "Resetting font cache"
    fc-cache -f $HOME/.fonts
fi



###########################################################################

section ">>> java"

sudo apt update && sudo apt install -y \
    default-jdk \
 && echo "java debian packages installed"








###########################################################################

section ">>> python"

sudo apt update && sudo apt install -y \
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
    # psycopg2 \
    # pgcli \
    grin \
    isort \
    pylint \
    radon \
    autopep8 \
    glances \
    radian \
 && echo "py_modules python packages installed"







###########################################################################

# section ">>> database"



# sudo apt update && sudo apt install -y \
#     libpq-dev \
#     postgresql-client-11 \
#     postgresql-11 \
#     postgresql-contrib \
#     postgresql-plpython3-11 \
#     postgresql-11-pllua \
#     luajit \
#     postgresql-11-pgtap \
#     pgtap \
#  && echo "database debian packages installed"






# echo "post-install scripts"
# sudo -u postgres createuser -s $USER
# sudo -u postgres createdb $USER



###########################################################################

section ">>> gui"



sudo apt update && sudo apt install -y \
    xorg \
    xserver-xorg-input-all \
    fonts-dejavu \
    gnome-icon-theme \
    awesome \
    i3 \
    xfce4-terminal \
    lxappearance \
    gtk2-engines \
    conky \
    scite \
    fslint \
    bleachbit \
 && echo "gui debian packages installed"








###########################################################################

section ">>> latex"



sudo apt update && sudo apt install -y \
    pandoc \
    lmodern \
    texlive-plain-generic \
    texlive-fonts-recommended \
    texlive-humanities \
    texlive-latex-extra \
    texlive-xetex \
    texinfo \
 && echo "latex debian packages installed"






echo "post-install scripts"
cd /usr/share/texlive/texmf-dist
sudo wget http://mirrors.ctan.org/install/fonts/inconsolata.tds.zip
sudo unzip inconsolata.tds.zip
sudo rm inconsolata.tds.zip
echo "Map zi4.map" | sudo tee --append /usr/share/texlive/texmf-dist/web2c/updmap.cfg
sudo mktexlsr
sudo updmap-sys









###########################################################################

# section ">>> docker"


# DOCKER=get-docker.sh
# curl -fsSL get.docker.com -o $DOCKER
# sudo sh $DOCKER
# sudo usermod -aG docker $USER
# rm $DOCKER

# echo "docker installed"





###########################################################################

section ">>> sublime-text"


echo "pre-install scripts"
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add
sudo apt install apt-transport-https
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list


sudo apt update && sudo apt install -y \
    sublime-text \
 && echo "sublime-text debian packages installed"


###########################################################################

section ">>> clang"


sudo sudo apt install -y \
    clang \
    clang-tidy \
 && echo "clang installed"








###########################################################################

section ">>> golang"


sudo sudo apt install -y \
    golang \
 && echo "golang installed"







###########################################################################

# section ">>> rust-lang"


# curl https://sh.rustup.rs -sSf | sh

# echo "rust-lang installed"





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

section ">>> rlang-debian"



sudo apt update && sudo apt install -y \
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
 && echo "rlang-debian debian packages installed"








###########################################################################

section ">>> rlang-bayesian"


sudo Rscript -e "install.packages(c('bayesplot', 'bridgesampling', 'brms', 'coda', 'rstan', 'rstanarm', 'rstantools', 'MCMCpack'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-regression"

sudo Rscript -e "install.packages(c('arm', 'car', 'caret', 'e1071', 'lme4', 'lmtest', 'visreg', 'Boruta'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-clustering"

sudo Rscript -e "install.packages(c('fpc', 'gclus', 'trimcluster'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-decision-trees"


sudo Rscript -e "install.packages(c('dtree', 'rpart.plot', 'party', 'partykit', 'randomForest', 'ranger', 'tree'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-graphs"

sudo Rscript -e "install.packages(c('DiagrammeR', 'ggiraph', 'igraph', 'influenceR', 'visNetwork', 'networkD3'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-jupyter"

sudo Rscript -e "install.packages(c('IRkernel'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-forecast"


sudo Rscript -e "install.packages(c('forecast', 'prophet', 'tseries', 'xts', 'zoo'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-microsoft"


sudo Rscript -e "install.packages(c('officer', 'openxlsx', 'WordR', 'rvg'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-text"


sudo Rscript -e "install.packages(c('tm', 'qdap'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-map"


sudo Rscript -e "install.packages(c('leaflet', 'geosphere', 'mapproj', 'maps', 'maptools', 'RgoogleMaps', 'ggmap'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-gantt"


sudo Rscript -e "install.packages(c('plan', 'projmanr', 'plotrix', 'timelineS', 'timevis', 'vistime'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-visual"


sudo Rscript -e "install.packages(c('corrplot', 'corrr', 'd3heatmap', 'dygraphs', 'ggalt', 'ggcorrplot', 'ggedit', 'ggExtra', 'ggfittext', 'ggfortify', 'ggplot2', 'ggrepel', 'ggridges', 'ggthemes', 'ggvis', 'gplots', 'grid', 'gridExtra', 'gtable', 'heatmaply', 'highcharter', 'metricsgraphics', 'plotly', 'qcc', 'qicharts2', 'rbokeh', 'RColorBrewer', 'scales', 'threejs', 'treemapify', 'vcd', 'venneuler', 'viridis', 'viridisLite', 'waffle', 'wesanderson'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-tidyverse"


sudo Rscript -e "install.packages(c('tidyverse', 'dplyr', 'dtplyr', 'forcats', 'glue', 'purrr', 'readr', 'readxl', 'reshape2', 'rlang', 'stringr', 'tibble', 'tidyr', 'tidyselect', 'usethis', 'widyr', 'withr'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-modelling"



sudo Rscript -e "install.packages(c('broom', 'gmodels', 'modelr', 'modeltools', 'recipes', 'dataPreparation'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-reporting"


sudo Rscript -e "install.packages(c('bookdown', 'brew', 'DT', 'flexdashboard', 'flextable', 'formattable', 'hrbrthemes', 'htmlTable', 'htmltools', 'htmlwidgets', 'janitor', 'kableExtra', 'knitr', 'labeling', 'pander', 'pixiedust', 'prettydoc', 'prettyunits', 'revealjs', 'rhandsontable', 'rmarkdown', 'rmdformats', 'rmdshower', 'rpivotTable', 'tables', 'tint', 'tufte', 'xaringan', 'xtable', 'wordcloud'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-testing"


sudo Rscript -e "install.packages(c('assertr', 'assertthat', 'covr', 'testthat'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-pkg"


sudo Rscript -e "install.packages(c('devtools', 'formatR', 'lintr', 'packrat', 'roxygen2', 'sinew', 'styler'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-shiny"


sudo Rscript -e "install.packages(c('shiny', 'shinyBS', 'shinydashboard', 'shinyjs', 'shinythemes'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-db"


sudo Rscript -e "install.packages(c('DBI', 'dbplyr', 'pool', 'RPostgres'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-text"


sudo Rscript -e "install.packages(c('snakecase', 'stringdist', 'stringi', 'textclean', 'tidytext', 'whisker', 'crayon'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-net"


sudo Rscript -e "install.packages(c('httr', 'RCurl', 'servr'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-protocols"


sudo Rscript -e "install.packages(c('data.table', 'data.tree', 'jsonlite', 'reticulate', 'yaml'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-finance"


sudo Rscript -e "install.packages(c('tidyquant', 'Quandl', 'finreportr'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-misctools"


sudo Rscript -e "install.packages(c('gdata', 'gtools', 'Hmisc', 'psych', 'arsenal', 'descriptr'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-time"


sudo Rscript -e "install.packages(c('hms', 'lubridate'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"




###########################################################################

section ">>> rlang-core"


sudo Rscript -e "install.packages(c('docopt'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"



###########################################################################

# section ">>> rstudio"


# sudo apt update && sudo apt install -y \
#     libjpeg62 \
#     libgstreamer1.0-0 \
#     libgstreamer-plugins-base1.0-0 \
#  && echo "rstudio debian packages installed"


# echo "post-install scripts"
# RSTUDIO=rstudio-1.2.5033-amd64.deb
# wget https://download1.rstudio.org/desktop/bionic/amd64/$RSTUDIO
# sudo dpkg -i $RSTUDIO
# rm $RSTUDIO
