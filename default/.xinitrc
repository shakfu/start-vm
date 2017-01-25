#!/usr/bin/env bash

#vmware-user &
vmware-user-suid-wrapper &

vmhgfs-fuse .host:/shared ~/.host-shared

(sleep 2s && conky -c ~/.config/conky/conky_start) &

exec awesome
#exec i3
