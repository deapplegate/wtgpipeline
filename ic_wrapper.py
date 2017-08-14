#!/usr/bin/env python
import sys

objname = sys.argv[1]
filter = sys.argv[2]
pprun = sys.argv[3]

r_ext = False
if len(sys.argv) > 4:
    star_suppression = sys.argv[4]
    if star_suppression == 'yes':
        r_ext = True
    

import calc_test_save

calc_test_save.run_correction(objname,filter,pprun,r_ext=r_ext)

