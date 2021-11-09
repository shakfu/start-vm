set nocompatible              " required
filetype off                  " required

" set the runtime path to include Vundle and initialize
set rtp+=~/.vim/bundle/Vundle.vim
call vundle#begin()

" alternatively, pass a path where Vundle should install plugins
"call vundle#begin('~/some/path/here')

" let Vundle manage Vundle, required
Plugin 'gmarik/Vundle.vim'

" add all your plugins here (note older versions of Vundle
" used Bundle instead of Plugin)

" ...

Plugin 'vim-scripts/indentpython.vim'
"Plugin 'vim-syntastic/syntastic'
Plugin 'nvie/vim-flake8'
Plugin 'kien/ctrlp.vim'
Plugin 'jnurmine/Zenburn'

Plugin 'keith/swift.vim'
Plugin 'gmoe/vim-faust'
Plugin 'rust-lang/rust.vim'
Plugin 'tidalcycles/vim-tidal'
Plugin 'luisjure/csound-vim'
Plugin 'ibab/vim-snakemake'
Plugin 'tbastos/vim-lua'
Plugin 'highwaynoise/chuck.vim'

" All of your Plugins must be added before the following line
call vundle#end()            " required
filetype plugin indent on    " required

set tabstop=4
set softtabstop=4
set shiftwidth=4
set textwidth=79
set expandtab
set autoindent
set fileformat=unix

set encoding=utf-8

syntax enable
set t_Co=256
"set cursorline

let python_highlight_all=1


let g:zenburn_transparent = 1
colorscheme zenburn

set background=dark

" enable/disable folding for csound
autocmd Syntax csound setlocal foldmethod=manual

" adding pd lua files to be recognized as lua files
autocmd BufNewFile,BufRead *.pd_lua set syntax=lua

autocmd FileType vim let b:vcm_tab_complete = 'vim'

let mapleader = ","
nnoremap <leader>e :w !python3 send.py<Enter><Enter>

