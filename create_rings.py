#!/usr/bin/env python
####################

import sys, os


if 'bonn' not in os.environ:
    os.environ['bonn'] = os.getcwd()+'/'

if 'subdir' not in os.environ:
    os.environ['subdir'] = '/nfs/slac/g/ki/ki05/anja/SUBARU'


cluster = sys.argv[1]
filter = sys.argv[2]
starfile = sys.argv[3]

offsetFile = 'fit'
if len(sys.argv) > 4:
    offsetFile = sys.argv[4]


import calc_test_save as cts

os.chdir(os.environ['bonn'])


cts.make_rings(cluster, filter, starfile, offsetFile)
