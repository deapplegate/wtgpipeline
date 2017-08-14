#!/usr/bin/env python

import sys, re
from datarobot import *


def find(exp):

    targets = Target.select(AND(AND(Target.q.RA >= ra - .5, Target.q.RA <= ra + .5),
                                AND(Target.q.DEC >= dec - .5, Target.q.DEC <= dec + .5)))

    if targets.count() == 0:
        print '\tNo Matches Found'
        return

    for target in targets:
        print '\tName: %s\tRA: %f\tDEC: %f' % (target.name, target.RA, target.DEC)
        for run in target.runs:
            print '\t\t%s %s' % (run.night, run.filter)


line = raw_input()
while line is not None and line is not '\n':

    line.strip()
    if Exposure.selectBy(expid=line).count() > 0:
        print 'True'
    else:
        print 'False'

    line = raw_input()
