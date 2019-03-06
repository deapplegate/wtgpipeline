#!/usr/bin/env python

#
# Python script to compare two lists.
# The first list (provided on stdin)
# is compared to a list given as first
# argument. File names contained in the
# second list are hereby removed from the
# first list (i.e. the remaining elements
# are written to stdout). Hereby, it
# is sufficient that the elements of the
# first list match substrings in the second
# list to be excluded. The script is used
# for the exlusion of certain chips in the
# superflat creation.

import glob
import string
import sys

excl_file = sys.argv[1]
exclList = []

try:
    f=open(excl_file, "r")
    for line in f.readlines():
        if len(line) > 2:
            exclList.append(line)
    f.close()
except IOError:
    None

for line in sys.stdin.readlines():
    match = 0
    for excl in exclList:
        if glob.fnmatch.fnmatch(line, "*"+excl[:-1]+"*"):
            match = 1
            break
    if not match:
        print line,
