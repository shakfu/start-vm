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
recipe "name: rlang"
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
echo "Install core debian_packages?"
echo "build-essential, cmake, ncdu, htop, vim, exuberant-ctags, tig, ranger, bmon, pv, rpl, unzip, p7zip-full, open-vm-tools"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
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
fi
###########################################################################
section ">>> java"
echo "Install java debian_packages?"
echo "default-jdk"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo apt-get update && sudo apt-get install -y \
    default-jdk \
 && echo "java debian packages installed"
fi
###########################################################################
section ">>> python"
echo "Install python debian_packages?"
echo "python3-dev, python3-setuptools, python3-pip"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo apt-get update && sudo apt-get install -y \
    python3-dev \
    python3-setuptools \
    python3-pip \
 && echo "python debian packages installed"
fi
###########################################################################
section ">>> py_modules"
echo "Install py_modules python_packages?"
echo "wheel, virtualenv, ipython, cython, psycopg2, pgcli, grin, isort, pylint, radon, autopep8, glances, rtichoke"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
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
    rtichoke \
 && echo "py_modules python packages installed"
fi
###########################################################################
section ">>> database"
echo "Install database debian_packages?"
echo "libpq-dev, postgresql-client-10, postgresql-10, postgresql-contrib-10, postgresql-plpython3-10, postgresql-10-pllua, luajit, postgresql-10-pgtap, pgtap"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo apt-get update && sudo apt-get install -y \
    libpq-dev \
    postgresql-client-10 \
    postgresql-10 \
    postgresql-contrib-10 \
    postgresql-plpython3-10 \
    postgresql-10-pllua \
    luajit \
    postgresql-10-pgtap \
    pgtap \
 && echo "database debian packages installed"
echo "post-install scripts"
sudo -u postgres createuser -s $USER
sudo -u postgres createdb $USER
fi
###########################################################################
section ">>> gui"
echo "Install gui debian_packages?"
echo "xorg, xserver-xorg-input-all, open-vm-tools-desktop, fonts-dejavu, gnome-icon-theme, awesome, i3, xfce4-terminal, lxappearance, gtk2-engines, conky, scite, gtkorphan, fslint, bleachbit"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
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
fi
###########################################################################
section ">>> latex"
echo "Install latex debian_packages?"
echo "pandoc, lmodern, texlive-generic-recommended, texlive-fonts-recommended, texlive-humanities, texlive-latex-extra, texlive-xetex, texinfo"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
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
fi
###########################################################################
section ">>> rlang-debian"
echo "Install rlang-debian debian_packages?"
echo "fonts-texgyre, libssl-dev, libxml2-dev, libcurl4-openssl-dev, libcairo2-dev, libxt-dev, libssh2-1-dev, r-base, r-base-dev, r-recommended"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
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
 && echo "rlang-debian debian packages installed"
fi
###########################################################################
section ">>> rlang-bayesian"
echo "Install rlang-bayesian rlang_packages?"
echo "bayesplot, bridgesampling, brms, coda, rstan, rstanarm, rstantools, MCMCpack"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('bayesplot', 'bridgesampling', 'brms', 'coda', 'rstan', 'rstanarm', 'rstantools', 'MCMCpack'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-regression"
echo "Install rlang-regression rlang_packages?"
echo "arm, car, caret, e1071, lme4, lmtest, visreg, Boruta"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('arm', 'car', 'caret', 'e1071', 'lme4', 'lmtest', 'visreg', 'Boruta'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-clustering"
echo "Install rlang-clustering rlang_packages?"
echo "fpc, gclus, trimcluster"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('fpc', 'gclus', 'trimcluster'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-decision-trees"
echo "Install rlang-decision-trees rlang_packages?"
echo "dtree, rpart.plot, party, partykit, randomForest, ranger, tree"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('dtree', 'rpart.plot', 'party', 'partykit', 'randomForest', 'ranger', 'tree'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-graphs"
echo "Install rlang-graphs rlang_packages?"
echo "DiagrammeR, ggiraph, igraph, influenceR, visNetwork, networkD3"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('DiagrammeR', 'ggiraph', 'igraph', 'influenceR', 'visNetwork', 'networkD3'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-jupyter"
echo "Install rlang-jupyter rlang_packages?"
echo "IRkernel"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('IRkernel'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-forecast"
echo "Install rlang-forecast rlang_packages?"
echo "forecast, prophet, tseries, xts, zoo"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('forecast', 'prophet', 'tseries', 'xts', 'zoo'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-microsoft"
echo "Install rlang-microsoft rlang_packages?"
echo "officer, openxlsx, WordR, rvg"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('officer', 'openxlsx', 'WordR', 'rvg'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-text"
echo "Install rlang-text rlang_packages?"
echo "tm, qdap"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('tm', 'qdap'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-map"
echo "Install rlang-map rlang_packages?"
echo "leaflet, geosphere, mapproj, maps, maptools, RgoogleMaps, ggmap"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('leaflet', 'geosphere', 'mapproj', 'maps', 'maptools', 'RgoogleMaps', 'ggmap'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-gantt"
echo "Install rlang-gantt rlang_packages?"
echo "plan, projmanr, plotrix, timelineS, timevis, vistime"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('plan', 'projmanr', 'plotrix', 'timelineS', 'timevis', 'vistime'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-visual"
echo "Install rlang-visual rlang_packages?"
echo "corrplot, corrr, d3heatmap, dygraphs, ggalt, ggcorrplot, ggedit, ggExtra, ggfittext, ggfortify, ggplot2, ggrepel, ggridges, ggthemes, ggvis, gplots, grid, gridExtra, gtable, heatmaply, highcharter, metricsgraphics, plotly, qcc, qicharts2, rbokeh, RColorBrewer, scales, threejs, treemapify, vcd, venneuler, viridis, viridisLite, waffle, wesanderson"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('corrplot', 'corrr', 'd3heatmap', 'dygraphs', 'ggalt', 'ggcorrplot', 'ggedit', 'ggExtra', 'ggfittext', 'ggfortify', 'ggplot2', 'ggrepel', 'ggridges', 'ggthemes', 'ggvis', 'gplots', 'grid', 'gridExtra', 'gtable', 'heatmaply', 'highcharter', 'metricsgraphics', 'plotly', 'qcc', 'qicharts2', 'rbokeh', 'RColorBrewer', 'scales', 'threejs', 'treemapify', 'vcd', 'venneuler', 'viridis', 'viridisLite', 'waffle', 'wesanderson'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-tidyverse"
echo "Install rlang-tidyverse rlang_packages?"
echo "tidyverse, dplyr, dtplyr, forcats, glue, purrr, readr, readxl, reshape2, rlang, stringr, tibble, tidyr, tidyselect, usethis, widyr, withr"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('tidyverse', 'dplyr', 'dtplyr', 'forcats', 'glue', 'purrr', 'readr', 'readxl', 'reshape2', 'rlang', 'stringr', 'tibble', 'tidyr', 'tidyselect', 'usethis', 'widyr', 'withr'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-modelling"
echo "Install rlang-modelling rlang_packages?"
echo "broom, gmodels, modelr, modeltools, recipes"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('broom', 'gmodels', 'modelr', 'modeltools', 'recipes'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-reporting"
echo "Install rlang-reporting rlang_packages?"
echo "bookdown, brew, DT, flexdashboard, flextable, formattable, hrbrthemes, htmlTable, htmltools, htmlwidgets, janitor, kableExtra, knitr, labeling, pander, pixiedust, prettydoc, prettyunits, revealjs, rhandsontable, rmarkdown, rmdformats, rmdshower, rpivotTable, tables, tint, tufte, xaringan, xtable, wordcloud"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('bookdown', 'brew', 'DT', 'flexdashboard', 'flextable', 'formattable', 'hrbrthemes', 'htmlTable', 'htmltools', 'htmlwidgets', 'janitor', 'kableExtra', 'knitr', 'labeling', 'pander', 'pixiedust', 'prettydoc', 'prettyunits', 'revealjs', 'rhandsontable', 'rmarkdown', 'rmdformats', 'rmdshower', 'rpivotTable', 'tables', 'tint', 'tufte', 'xaringan', 'xtable', 'wordcloud'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-testing"
echo "Install rlang-testing rlang_packages?"
echo "assertr, assertthat, covr, testthat"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('assertr', 'assertthat', 'covr', 'testthat'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-pkg"
echo "Install rlang-pkg rlang_packages?"
echo "devtools, formatR, lintr, packrat, roxygen2, sinew, styler"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('devtools', 'formatR', 'lintr', 'packrat', 'roxygen2', 'sinew', 'styler'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-shiny"
echo "Install rlang-shiny rlang_packages?"
echo "shiny, shinyBS, shinydashboard, shinyjs, shinythemes"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('shiny', 'shinyBS', 'shinydashboard', 'shinyjs', 'shinythemes'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-db"
echo "Install rlang-db rlang_packages?"
echo "DBI, dbplyr, pool, RPostgres"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('DBI', 'dbplyr', 'pool', 'RPostgres'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-text"
echo "Install rlang-text rlang_packages?"
echo "snakecase, stringdist, stringi, textclean, tidytext, whisker, crayon"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('snakecase', 'stringdist', 'stringi', 'textclean', 'tidytext', 'whisker', 'crayon'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-net"
echo "Install rlang-net rlang_packages?"
echo "httr, RCurl, servr"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('httr', 'RCurl', 'servr'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-datastructures"
echo "Install rlang-datastructures rlang_packages?"
echo "data.table, data.tree, jsonlite, reticulate, yaml"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('data.table', 'data.tree', 'jsonlite', 'reticulate', 'yaml'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-misctools"
echo "Install rlang-misctools rlang_packages?"
echo "gdata, gtools, Hmisc, psych, arsenal, descriptr"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('gdata', 'gtools', 'Hmisc', 'psych', 'arsenal', 'descriptr'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-time"
echo "Install rlang-time rlang_packages?"
echo "hms, lubridate"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('hms', 'lubridate'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rlang-core"
echo "Install rlang-core rlang_packages?"
echo "docopt"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
sudo Rscript -e "install.packages(c('docopt'), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
fi
###########################################################################
section ">>> rstudio"
echo "Install rstudio debian_packages?"
echo "libjpeg62, libgstreamer1.0-0, libgstreamer-plugins-base1.0-0"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
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
fi
###########################################################################
section ">>> docker"
echo "Install docker?"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
DOCKER=get-docker.sh
curl -fsSL get.docker.com -o $DOCKER
sudo sh $DOCKER
sudo usermod -aG docker $USER
rm $DOCKER
echo "docker installed"
fi
###########################################################################
section ">>> sublime-text"
echo "Install sublime-text debian_packages?"
echo "sublime-text"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
echo "pre-install scripts"
wget -qO - https://download.sublimetext.com/sublimehq-pub.gpg | sudo apt-key add
sudo apt-get install apt-transport-https
echo "deb https://download.sublimetext.com/ apt/stable/" | sudo tee /etc/apt/sources.list.d/sublime-text.list
sudo apt-get update && sudo apt-get install -y \
    sublime-text \
 && echo "sublime-text debian packages installed"
fi
###########################################################################
section ">>> golang"
echo "Install golang?"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
GOLANG=go1.9.2.linux-amd64.tar.gz
wget https://redirector.gvt1.com/edgedl/go/$GOLANG
sudo tar -C /usr/local -xzf $GOLANG
rm -rf $GOLANG
echo "golang installed"
fi
###########################################################################
section ">>> rust-lang"
echo "Install rust-lang?"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
curl https://sh.rustup.rs -sSf | sh
echo "rust-lang installed"
fi
###########################################################################
section ">>> powerline-fonts"
echo "Install powerline-fonts?"
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
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
fi