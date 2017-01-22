
sudo apt-get update && apt-get install -y \
    build-essential \
    ncdu \
    htop \
    vim \
    exuberant-ctags \
    git \
    tig \
    ranger \
    bmon \
    pv \
    rpl \
    unzip \
    p7zip-full \
    libpq-dev \
    open-vm-tools \
    open-vm-tools-desktop \
    python3-dev \
    python3-setuptools \
    python3-pip \
    xorg \
    fonts-dejavu \
    gnome-icon-theme \
    i3-wm \
    roxterm \
    lxappearance \
    gtk2-engines \
    conky \
    scite \
    gtkorphan \
    fslint \
    bleachbit \
 && echo "debian packages installed"

sudo apt-get purge -y \
    xserver-xorg-input-all \
    xserver-xorg-input-synaptics \
    xserver-xorg-input-wacom \
    xserver-xorg-video-all \
    xserver-xorg-video-ati \
    xserver-xorg-video-cirrus \
    xserver-xorg-video-geode \
    xserver-xorg-video-mach64 \
    xserver-xorg-video-mga \
    xserver-xorg-video-neomagic \
    xserver-xorg-video-nouveau \
    xserver-xorg-video-openchrome \
    xserver-xorg-video-r128 \
    xserver-xorg-video-radeon \
    xserver-xorg-video-savage \
    xserver-xorg-video-siliconmotion \
    xserver-xorg-video-sisusb \
    xserver-xorg-video-tdfx \
    xserver-xorg-video-trident \
 && echo "debian packages purged"

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
 && echo "python packages installed"


