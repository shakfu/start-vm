#!/usr/bin/env bash


vmware-user &

(sleep 2s && ~/.conky/conky_start) &

tilda &

#xrandr -s 1024x768 -d 96

exec awesome



