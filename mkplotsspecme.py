import os
import MySQLdb
import os, sys, anydbm, time
#from config import datb, dataloc
#db = anydbm.open("./db/" + cluster,'c')
import lib 
#lib.galextinct(cluster, db)
#db[sys.argv[0][:-3]] = 'Started/' + time.asctime()

spectype = 'full'
if len(sys.argv) > 2:
    if sys.argv[2] == 'spec': spectype = 'spec'

listfile = []

import os
import MySQLdb
colnames = ['B','V','R','I','z']
kfile = open('lk.sm','w')
kfile.write("device postlandfile spec.ps\nerase macro read plotbpz zs\ndevice x11\n")
legendlist = []
varps = []
bl1 = 0
bl2 = 0
file = open(sys.argv[1],'r').readlines()
results = []
for line in file:

    if line[0] != '#':
        import re                   
        res = re.split('\s+',line)
        for i in range(len(res)):
            print res[i],i
        #results.append([float(res[2]),float(res[48])]) # OLD
        results.append([float(res[2]),float(res[23])])
        #raw_input()
diff = []
z = []
z_spec = []
print results[0:3]
for line in results:
    diff_val = (line[0] - line[1])/(1 + line[1])
    if 1==1: #(0.48 > float(line[1])  or float(line[1]) > 0.53):
        print line, spectype                           
        diff.append(diff_val)
        z.append(line[0])
        z_spec.append(line[1])

list = diff[:]  
import pylab    
from scipy import arange
a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.016))
print a,b,varp
varps.append(varp[0])
#pylab.legend(varps,legendlist)

import scipy

diffB = []
for d in diff:
    if abs(d) < 0.1:
        diffB.append(d)
diff = diffB

list = scipy.array(diff)


mu = list.mean()
sigma = list.std()


print 'mu', mu
print 'sigma', sigma

#print 'std', scipy.std(a)
#print 'mean', scipy.mean(a)

from scipy import stats
#x = scipy.linspace(list.min(), list.max(), 100)
pdf = scipy.stats.norm.pdf(b, mu, sigma)
print 'pdf', pdf
#s = subplot(111) 

height = scipy.array(a).max()

pylab.plot(b,len(diff)*pdf/pdf.sum(),'r')

pylab.xlabel("(PhotZ - SpecZ)/(1 + SpecZ)")
pylab.ylabel("Number of Galaxies")
pylab.savefig('RedshiftErrors.ps')
pylab.clf()

pylab.scatter(z_spec,diff)
pylab.xlim(0,1)
pylab.ylim(-0.5,0.5)
pylab.ylabel("(PhotZ - SpecZ)/(1 + SpecZ)")
pylab.xlabel("PhotZ")
pylab.savefig('RedshiftScatter.ps')
