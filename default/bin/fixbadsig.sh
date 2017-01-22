# if this doesn't work
# sudo rm -fR /var/lib/apt/lists/*
# try this
# sudo aptitude -o Acquire::http::No-Cache=True -o Acquire::BrokenProxy=true update
