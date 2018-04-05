#!/usr/bin/env bash

#vmware-user &
vmware-user-suid-wrapper &

vmhgfs-fuse .host:/shared ~/.host-shared


(sleep 2s && conky -c ~/.config/conky/conky_start) &

setxkbmap -rules evdev -model apple_laptop -layout us,ara -variant mac,mac -option grp:alt_shift_toggle

/usr/bin/xmodmap /home/$USER/.Xmodmap

exec awesome
#exec i3


