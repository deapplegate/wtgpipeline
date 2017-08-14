import os, sys, anydbm, time
import lib, scipy, pylab 
from scipy import arange
                                                                                                       

results_e = []
results_b = []
anjaplot = open('anjaplot','w')
anjaplot.write('# Z_PHOT Z_MIN Z_MAX ODDS Z_SPEC\n')


diff = []
z = []
z_spec = []

file = open('./OUTPUT/photz.zout','r').readlines()
for line in file:
    if line[0] != '#':
        import re                                     
        res = re.split('\s+',line)
        if res[0] == '': res = res[1:]
        anjaplot.write(res[1] + ' ' + res[2] + ' ' + res[3] + ' ' + res[5] + ' ' + res[9] + '\n') 
        results_b.append([float(res[1]),float(res[9])])

file = open('HDFN.APER1.CWWSB_capak.list.1.spec.bpz','r').readlines()
for line in file:
    if line[0] != '#':
        import re                                     
        res = re.split('\s+',line)
        if res[0] == '': res = res[1:]
        results_e.append([float(res[2]),float(res[1])])

import pylab
pylab.scatter(scipy.array(results_e)[:,0],scipy.array(results_b)[:,0])
pylab.show()
