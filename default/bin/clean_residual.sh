sudo apt-get remove --purge $(sudo dpkg -l | grep "^rc" | awk '{print $2}' | tr '\n' ' ')
