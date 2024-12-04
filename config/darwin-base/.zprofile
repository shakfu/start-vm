eval "$(/opt/homebrew/bin/brew shellenv)"

export CLICOLOR=1
export LSCOLORS=gxBxhxDxfxhxhxhxhxcxcx

export HOMEBREW_NO_ANALYTICS=1
export HOMEBREW_NO_GITHUB_API=1
export HOMEBREW_NO_INSECURE_REDIRECT=1
export HOMEBREW_NO_AUTO_UPDATE=1
export EDITOR="/usr/local/bin/subl"

export PDDIR="/Applications/Studio/Pd-0.55-0.app/Contents/Resources"

export PATH=$HOME/.local/bin:$HOME/.opt/zig:/opt/quarto/bin:$HOME/Library/Python/3.12/bin:$PDDIR/bin:$PATH

export BUN_INSTALL="$HOME/.bun"
export PATH="$BUN_INSTALL/bin:$PATH"

export GOPATH=$HOME/.opt/golang
export GOROOT=/opt/homebrew/opt/go/libexec
export PATH=$PATH:$GOPATH/bin
export PATH=$PATH:$GOROOT/bin

export DENO_INSTALL="$HOME/.deno"
export PATH="$DENO_INSTALL/bin:$PATH"

export BAT_THEME="zenburn"
export RUSTC_WRAPPER=sccache

alias cdp='cd $HOME/Downloads/src/py-js/source/py'
alias cd..='cd ..'
alias ..='cd ..'
alias ...='cd ../../../'
alias ....='cd ../../../../'
alias .....='cd ../../../../'
alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'
alias bc='bc -l'
alias sha1='openssl sha1'
alias h='history'
alias j='jobs -l'
alias path='echo -e ${PATH//:/\\n}'
alias now='date +"%T"'
alias nowtime=now
alias nowdate='date +"%d-%m-%Y"'
alias ping='ping -c 5'
alias fastping='ping -c 100 -s.2'
alias ports='netstat -tulanp'
alias wget='wget -c'
alias df='df -H'
alias du='du -ch'
alias cpsync="rsync --progress -ravz"
alias rmq="sudo /usr/bin/xattr -r -d com.apple.quarantine"

alias ls="ls -GFh"
alias ll="ls -lG"
alias la="ls -a"

alias i="ipython -i"
alias pinstall="pip3 install --user --break-system-packages --upgrade"
alias punstall="pip3 uninstall --break-system-packages"
alias work="subl . && and open ."

alias outdated='pip3 list --outdated'
alias update='brew update && brew upgrade'
alias f='grep -rl'
alias gs='git status'
alias ga='git add --all .'
alias gc='git commit -m'
alias gp='git push'
alias gd='git diff'
alias gco='git checkout'
alias dm='youtube-dl -f 140'
alias r='radian'
#alias cat='bat'
alias startdb='pg_ctl -D /usr/local/var/postgres start'
alias stopdb='pg_ctl -D /usr/local/var/postgres stop'
#alias pd='${PDDIR}/bin/pd'
alias clone='git clone --depth=1 --recurse-submodules --shallow-submodules'
alias cfmt='clang-format -i'
alias sclang='/Applications/Studio/SuperCollider/SuperCollider.app/Contents/MacOS/sclang'
alias gaa='git add --all .'
alias gcm='git commit -m'
alias sleepnow='pmset sleepnow'

bindkey "^[[H" beginning-of-line
bindkey "^[[F" end-of-line

function depcheck {
    for f in $(ls)
    do
        otool -L $f
        echo
    done
}

function workon {
    complete -W "\`grep -oE '^[a-zA-Z0-9_.-]+:([^=]|$)' ?akefile | sed 's/[^a-zA-Z0-9_.-]*$//'\`" make
    subl $1
    open $1
    cd $1
}

function shrink_b {
    target=$(echo "$1" | sed 's:/*$::')
    #echo "${target}"
    #echo "${target}__tmp"
    ditto --arch `uname -m` "${target}" "${target}__tmp"
    rm -rf "${target}"
    mv "${target}__tmp" "${target}"
}

function rename_samples {
    python3 -c "import os; for i, o in enumerate(os.listdir('.')): os.rename(o,
f's{i:02d}.wav')"
}


export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion
