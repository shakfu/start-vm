#!

#rsync -avs -h -i --delete --dry-run src dst

#sudo rsync -avsih --delete /home/sa/PDFs /tmp/store

# -a archive mode: recursive with symbolic links and file perms
# -v verbose
# -z compression
# -s allow spaces in filenames
# -i itemize changes
# -h human readable summary


rsync -avzsih --delete $1 $2
