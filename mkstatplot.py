import pickle

t = open('store','r')
o = pickle.Unpickler(t)
w = o.load()

print w
ind = w.keys()
ws = sorted([float(x) for x in w[ind[0]].keys()])
print ws
import scipy
chis = scipy.zeros(len(ws)) 
print w.keys()

for key in w.keys():
    if key != 'MACS2214-13':
        for s in range(len(ws)):
            chis[s] += w[key][str(int(ws[s]))]
    
print chis
import pylab, math

pylab.plot(ws,math.e**(-1.*chis))

print key, w[key] 
#pylab.plot(ws,chis)
pylab.show()
