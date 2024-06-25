#!/usr/bin/env sh

COLOR_BOLD_YELLOW="\033[1;33m"
COLOR_BOLD_BLUE="\033[1;34m"
COLOR_BOLD_MAGENTA="\033[1;35m"
COLOR_BOLD_CYAN="\033[1;36m"
COLOR_RESET="\033[m"

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

recipe "name: base"
echo "platform: darwin"
echo

###########################################################################

section ">>> core"

brew update && brew upgrade && brew install \
	bat \
	bdw-gc \
	bison \
	boost \
	clang-format \
	cmake \
	cppcheck \
	czmq \
	d2 \
	ddh \
	difftastic \
	diskus \
	dprint \
	dua-cli \
	dust \
	fclones \
	fd \
	flac \
	flex \
	fzf \
	go-task \
	helix \
	highway \
	htop \
	hyperfine \
	lame \
	liblo \
	libogg \
	libsamplerate \
	libsndfile \
	libsoundio \
	libsoxr \
	libvorbis \
	marksman \
	ninja \
	opus \
	opusfile \
	pcre2 \
	portaudio \
	portmidi \
	ripgrep \
	rlwrap \
	rubberband \
	sk \
	sox \
	speex \
	sqlite \
	tree \
	typst \
	wget \
	xcodegen \
	zstd &&
	echo "homebrew packages installed"
