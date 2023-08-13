# ~/.bashrc: executed by bash(1) for non-login shells.
# see /usr/share/doc/bash/examples/startup-files (in the package bash-doc)
# for examples

COLOR_BOLD_YELLOW="\033[1;33m"
COLOR_BOLD_BLUE="\033[1;34m"
COLOR_BOLD_MAGENTA="\033[1;35m"
COLOR_BOLD_CYAN="\033[1;36m"
COLOR_BOLD_RED="\033[1;31m"
COLOR_BOLD_WHITE="\e[1m"
COLOR_RESET="\033[m"

# If not running interactively, don't do anything
[ -z "$PS1" ] && return

# don't put duplicate lines in the history. See bash(1) for more options
# don't overwrite GNU Midnight Commander's setting of `ignorespace'.
export HISTCONTROL=$HISTCONTROL${HISTCONTROL+,}ignoredups
# ... or force ignoredups and ignorespace
export HISTCONTROL=ignoreboth

# append to the history file, don't overwrite it
shopt -s histappend

# for setting history length see HISTSIZE and HISTFILESIZE in bash(1)

# check the window size after each command and, if necessary,
# update the values of LINES and COLUMNS.
shopt -s checkwinsize

# make less more friendly for non-text input files, see lesspipe(1)
[ -x /usr/bin/lesspipe ] && eval "$(SHELL=/bin/sh lesspipe)"

# set variable identifying the chroot you work in (used in the prompt below)
if [ -z "$debian_chroot" ] && [ -r /etc/debian_chroot ]; then
    debian_chroot=$(cat /etc/debian_chroot)
fi

# set a fancy prompt (non-color, unless we know we "want" color)
case "$TERM" in
    xterm-color) color_prompt=yes;;
esac

# uncomment for a colored prompt, if the terminal has the capability; turned
# off by default to not distract the user: the focus in a terminal window
# should be on the output of commands, not on the prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if [ -x /usr/bin/tput ] && tput setaf 1 >&/dev/null; then
	# We have color support; assume it's compliant with Ecma-48
	# (ISO/IEC-6429). (Lack of such support is extremely rare, and such
	# a case would tend to support setf rather than setaf.)
	color_prompt=yes
    else
	color_prompt=
    fi
fi

if [ "$color_prompt" = yes ]; then
    PS1='${debian_chroot:+($debian_chroot)}\[\033[01;32m\]\u@\h\[\033[00m\]:\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='${debian_chroot:+($debian_chroot)}\u@\h:\w\$ '
fi
unset color_prompt force_color_prompt

# If this is an xterm set the title to user@host:dir
case "$TERM" in
xterm*|rxvt*)
    PS1="\[\e]0;${debian_chroot:+($debian_chroot)}\u@\h: \w\a\]$PS1"
    ;;
*)
    ;;
esac

# Alias definitions.
# You may want to put all your additions into a separate file like
# ~/.bash_aliases, instead of adding them here directly.
# See /usr/share/doc/bash-doc/examples in the bash-doc package.

#if [ -f ~/.bash_aliases ]; then
#    . ~/.bash_aliases
#fi

# enable color support of ls and also add handy aliases
if [ -x /usr/bin/dircolors ]; then
    eval "`dircolors -b`"
    alias ls='ls --color=auto'
    alias dir='dir --color=auto'
    alias vdir='vdir --color=auto'

    alias grep='grep --color=auto'
    alias fgrep='fgrep --color=auto'
    alias egrep='egrep --color=auto'
fi

# some more ls aliases
alias ll='ls -lh'
alias la='ls -A'
alias l='ls -CF'

alias r='radian'
alias p='vim +NERDTree'
alias c='clear'                             # clear screen
alias f='find | grep'                       # quick file search
alias sps='ps aux | grep -v grep | grep'    # search processes
alias free='free -m'                        # show free mem in mb
alias path='echo -e ${PATH//:/\\n}'
alias ncduv='cd / && sudo ncdu --exclude=$HOME/.host-shared'
alias pinstall='pip3 install --user --break-system-packages --upgrade'

# interactive line wrapping
alias i='ipython -i'
alias lpsql="psql -L ~/psql.log"
#alias git='hub'
alias gitlog='git log --pretty=oneline --abbrev-commit'
alias mp3get='youtube-dl --extract-audio --audio-format mp3'
alias outdated='pip3 list --format=columns --outdated'

# Computer cleanup
alias cleanup='sudo apt-get -y autoclean && sudo apt-get -y autoremove && sudo apt-get -y clean && sudo apt-get -y remove && sudo deborphan | xargs sudo apt-get -y remove --purge'
# purge configuration files of removed packages on debian systems
alias configpurge="sudo aptitude purge `dpkg --get-selections | grep deinstall | awk '{print $1}'`"	
# remove all unused Linux Kernel headers, images & modules
alias kernelcleanup="dpkg -l 'linux-*' | sed '/^ii/!d;/'"$(uname -r | sed "s/\(.*\)-\([^0-9]\+\)/\1/")"'/d;s/^[^ ]* [^ ]* \([^ ]*\).*/\1/;/[0-9]/!d' | xargs sudo apt-get -y purge"
alias orphaned='sudo deborphan | xargs sudo apt-get -y remove --purge'

# docker aliases
# --------------
# Kill all running containers.
alias dockerkillall='docker kill $(docker ps -q)'

# Delete all stopped containers.
alias dockercleanc='printf "\n>>> Deleting stopped containers\n\n" && docker rm $(docker ps -a -q)'

# Delete all untagged images.
alias dockercleani='printf "\n>>> Deleting untagged images\n\n" && docker rmi $(docker images -q -f dangling=true)'

# Delete all stopped containers and untagged images.
alias dockerclean='dockercleanc || true && dockercleani'

# Remove all dangling volumes
alias dockercleanv='docker volume ls -qf dangling=true | xargs -r docker volume rm'

# Get last container id
alias dl='docker ps -l -q'

# simply docker run
alias drun='docker run -it --rm'

# simply docker-compose build
alias dbuild='docker-compose -f build.yml build'

# enable programmable completion features (you don't need to enable
# this, if it's already enabled in /etc/bash.bashrc and /etc/profile
# sources /etc/bash.bashrc).
if [ -f /etc/bash_completion ]; then
    . /etc/bash_completion
fi

# setup virtualenvs and pip
#export JAVA_HOME=/usr/lib/jvm/default-java
export GOPATH="$HOME/projects/gocode"
export EDITOR=vi
export BROWSER=/usr/bin/firefox
export PATH="$HOME/bin:$HOME/.local/bin:$HOME/.cargo/bin:/usr/local/go/bin:$GOPATH/bin:$PATH"
export LD_LIBRARY_PATH="/usr/lib/R/lib:/usr/lib/x86_64-linux-gnu:/usr/lib/jvm/default-java/jre/lib/amd64/server"

# fix keyboar layout for macbook pro on ubuntu server
#xmodmap -e "keycode 49 = section plusminus section plusminus section plusminus"
#xmodmap -e "keycode 94 = grave asciitilde grave asciitilde dead_grave dead_horn"



# functions
e() {
    scite $@ &
}

writezeros() {
    sudo dd if=/dev/zero of=/empty_file; sudo rm /empty_file
}



extract () {
    if [ -f $1 ] ; then
        case $1 in
            *.tar.bz2)  tar xjf $1      ;;
            *.tar.gz)   tar xzf $1      ;;
            *.bz2)      bunzip2 $1      ;;
            *.rar)      unrar x $1      ;;
            *.gz)       gunzip $1       ;;
            *.tar)      tar xf $1       ;;
            *.tbz2)     tar xjf $1      ;;
            *.tgz)      tar xzf $1      ;;
            *.zip)      unzip $1        ;;
            *.ZIP)      unzip $1        ;;
            *.Z)        uncompress $1   ;;
            *)          echo "'$1' cannot be extracted via extract()" ;;
        esac
    else
        echo "'$1' is not a valid file"
    fi
}

# mkmine - recursively change ownership to $USER:$USER
# usage:  mkmine, or
#         mkmine <filename | dirname>
function mkmine() { sudo chown -R ${USER}:${USER} ${1:-.}; }

# sanitize - set file/directory owner and permissions to normal values (644/755)
# usage: sanitize <file>
sanitize()
{
  chmod -R u=rwX,go=rX "$@"
  chown -R ${USER}:users "$@"
}

# start, stop, restart, reload - simple daemon management
# usage: start <daemon-name>
start()
{
  for arg in $*; do
    sudo /etc/rc.d/$arg start
  done
}
stop()
{
  for arg in $*; do
    sudo /etc/rc.d/$arg stop
  done
}
restart()
{
  for arg in $*; do
    sudo /etc/rc.d/$arg restart
  done
}
reload()
{
  for arg in $*; do
    sudo /etc/rc.d/$arg reload
  done
}




function fn_exists()
{
    type $1 | grep -q 'shell function'
}

function section {
    echo
    echo -e $COLOR_BOLD_MAGENTA$1 $COLOR_RESET
    echo "----------------------------------------------------------"
}

function warn {
    echo
    echo -e $COLOR_BOLD_RED"WARNING: "$COLOR_RESET$1
    echo
}

function finished {
    echo
    echo -e $COLOR_BOLD_WHITE"[DONE]"$COLOR_RESET
    echo
}

function info {
    echo
    echo -e "$COLOR_BOLD_CYAN$1 $COLOR_RESET"
    echo
}

function runtime {
    echo
    echo "----------------------------------------------------------"
    echo -e "=> $COLOR_BOLD_CYAN RUNTIME:$COLOR_RESET $COLOR_BOLD_WHITE$1$COLOR_RESET seconds"
    echo "----------------------------------------------------------"
    echo
}

function load_sql_dir {
    for target in $(ls $1)
    do
        echo "loading $1/$target"
        psql -f $1/$target
    done
}


function clean_if_not_empty {
    if [ "$(ls -A $1)" ]; then
         echo "cleaning $1"
         rm $1/*
    else
        echo "."
    fi
}


function safelink {
    if [ ! -e  $2 ]; then
        sudo ln -s $1 $2
    else
        warn "$2 already exists"
    fi
}

function overlink {
    if [ ! -e  $2 ]; then
        sudo ln -s $1 $2
    else
        warn "$2 already exists, overwriting it"
        sudo rm $2
        sudo ln -s $1 $2
    fi
}

function ptestkill {
    pgrep -f $1 > /dev/null
    if [ $? -eq 0 ]; then
      warn "$1 process is running. killing it"
      pkill -9 -f $1
    else
      echo "."
    fi
}

# clean non-essential files
function clean {
    find . \( -name \*.pyc -o -name \*.pyo -o -name \*.DS_Store -o -name __pycache__ \) -prune -exec rm -rf {} + 
}





