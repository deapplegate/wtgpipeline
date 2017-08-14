import MySQLdb
import os, sys, anydbm, time
import lib, scipy, pylab 
from scipy import arange

file = open(sys.argv[1],'r').readlines()
results = []
for line in file:
    if line[0] != '#':
        import re                   
        res = re.split('\s+',line)
        #for i in range(len(res)):
        #    print res[i],i
        results.append([float(res[2]),float(res[23]),res[1]])

diff = []
z = []
z_spec = []
for line in results:
    diff_val = (line[0] - line[1])/(1 + line[1])
    diff.append(diff_val)
    z.append(line[0])
    z_spec.append(line[1])

list = diff[:]  
import pylab   
varps = [] 
a, b, varp = pylab.hist(diff,bins=arange(-0.2,0.2,0.016))
#print a,b,varp
varps.append(varp[0])

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

reject = []
for line in results:
    diff_val = (line[0] - line[1])/(1 + line[1])
    if abs(diff_val)>2.*sigma: reject.append(line[2])

print reject

from scipy import stats
pdf = scipy.stats.norm.pdf(b, mu, sigma)
print 'pdf', pdf

height = scipy.array(a).max()

pylab.plot(b,len(diff)*pdf/pdf.sum(),'r')

pylab.xlabel("(PhotZ - SpecZ)/(1 + SpecZ)")
pylab.ylabel("Number of Galaxies")
pylab.show()
pylab.savefig('RedshiftErrors.ps')
pylab.clf()

pylab.scatter(z_spec,diff)
pylab.xlim(0,1)
pylab.ylim(-0.5,0.5)
pylab.ylabel("(PhotZ - SpecZ)/(1 + SpecZ)")
pylab.xlabel("PhotZ")
pylab.savefig('RedshiftScatter.ps')
