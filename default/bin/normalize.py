#!/usr/bin/env python

import hashlib
import os
import sys
from datetime import datetime

HASH = hashlib.md5(str(datetime.now()).encode()).hexdigest()

def normalize(path, file_func=None, dir_func=None):
    ''' recursive normalization of directory and file names

        applies the following changes to directory and filenames:

        - lowercasing

        - converts spaces to '-'
    '''
    norm_func = lambda x: x.lower().replace(' ', '-')
    if not file_func:
        file_func = norm_func
    if not dir_func:
        dir_func = norm_func
    for root, dirs, files in os.walk(path, topdown=False):
        for name in files:
            f = os.path.join(root, name)
            print(file_func(f))
        for name in dirs:
            d = os.path.join(root, name)
            #print(dir_func(d))


def norm_func(path):
    entry = os.path.basename(path)
    parent = os.path.dirname(path)
    entry_norm = entry.lower().replace(' ', '-')
    # Use proper suffix removal instead of strip() which removes characters
    p = os.path.join(parent, entry_norm) + HASH
    os.rename(path, p)
    # Remove the hash suffix properly
    new = p[:-len(HASH)] if p.endswith(HASH) else p
    os.rename(p, new)
    return new


def norm_path(path=None):
    if not path:
        path = sys.argv[1]
    normalize(path, norm_func)
    #normalize(path, None, norm_func)


if __name__ == '__main__':
    norm_path()
