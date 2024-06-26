#!/usr/bin/env sh

COLOR_BOLD_YELLOW="\033[1;33m"
COLOR_BOLD_BLUE="\033[1;34m"
COLOR_BOLD_MAGENTA="\033[1;35m"
COLOR_BOLD_CYAN="\033[1;36m"
COLOR_RESET="\033[m"

CONFIG=config/{{config}}
DEFAULT=default
CONFIG_DST=$HOME/.config
BIN=$HOME/bin

recipe() {
    echo
    echo -e $COLOR_BOLD_MAGENTA$1 $COLOR_RESET
    echo "=========================================================="
}

section() {
    echo
    echo -e $COLOR_BOLD_CYAN$1 $COLOR_RESET
    echo "----------------------------------------------------------"
}

install_default() {
    echo "installing $1"
    cp -rf $DEFAULT/$1 $HOME/
}

install_config() {
    echo "installing $1"
    cp -rf $CONFIG/$1 $CONFIG_DST/
}

recipe "name: {{name}}"
echo "platform: {{platform}}"
echo

section ">>> installing default dotfiles"
{% for entry in defaults %}
install_default {{entry}}
{% endfor %}

section ">>> installing .config folders"
if [ ! -d "$CONFIG_DST" ]; then
    mkdir -p $CONFIG_DST
fi
{% for entry in configs %}
install_config {{entry}}
{% endfor %}

{% for section in sections %}

###########################################################################

section ">>> {{section.name}}"

{% if conditional %}
{% if section.type == "shell" %}
echo "Install {{section.name}}?"
{% else %}
echo "Install {{section.name}} {{section.type}}?"
echo "{{section.install | join(', ')}}"
{% endif %}
read -p "Are you sure? " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
{% endif %}

{% if section.pre_install %}
echo "pre-install scripts"
{{section.pre_install}}
{% endif %}

{% if section.type == "debian_packages" %}
sudo apt-get update && sudo apt-get install -y \
{% for package in section.install %}
    {{package}} \
{% endfor %}
 && echo "{{section.name}} debian packages installed"
{% endif %}

{% if section.type == "python_packages" %}
sudo -H pip3 install \
{% for package in section.install %}
    {{package}} \
{% endfor %}
 && echo "{{section.name}} python packages installed"
{% endif %}

{% if section.type == "ruby_packages" %}
sudo gem install \
{% for package in section.install %}
    {{package}} \
{% endfor %}
 && echo "{{section.name}} ruby packages installed"
{% endif %}

{% if section.type == "rust_packages" %}
cargo install \
{% for package in section.install %}
    {{package}} \
{% endfor %}
 && echo "{{section.name}} rust packages installed"
{% endif %}

{% if section.type == "shell" %}
{{section.install}}
echo "{{section.name}} installed"
{% endif %}

{% if section.type == "rlang_packages" %}
sudo Rscript -e "install.packages(c({{section.install | sequence}}), repos='http://cran.rstudio.com/')" \
 && echo "rlang packages installed"
{% endif %}

{% if section.type == "homebrew_packages" %}
brew update && brew upgrade && brew install \
{% for package in section.install %}
    {{package}} \
{% endfor %}
 && echo "homebrew packages installed"
{% endif %}

{% if section.purge %}
sudo apt-get purge -y \
{% for package in section.purge %}
    {{package}} \
{% endfor %}
 && echo "{{section.name}} packages purged"
{% endif %}

{% if section.post_install %}
echo "post-install scripts"
{{section.post_install}}
{% endif %}

{% if conditional %}
fi
{% endif %}
{% endfor %}
