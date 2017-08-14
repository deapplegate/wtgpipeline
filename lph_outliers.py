#!/usr/bin/env python
import numpy
import sys 
import re, os
import pylab

def meanstdv(x):
    from math import sqrt
    n, mean, std = len(x), 0, 0
    for a in x:
        mean = mean + a
    mean = mean / float(n)
    for a in x:
        std = std + (a - mean)**2
    std = sqrt(std / float(n-1))
    return mean, std 

def doit(file,sourcefile):
    # assume the lephare structure.

    objects=open(file,'r').readlines()

    i=0
    l=[]
    k=[]
    for line in objects:
#        print i, line
        entries=re.split('\s+',line)
        # print entries
        if len(entries)<20:
            continue
#        print 'more than 20'
#        print entries[0], entries[1]
        if entries[0].find("#")!=-1 or  entries[1].find("#")!=-1:
            continue
        # print ' not commented ',entries[2] ,  entries[3],(entries[23]) 
#        print entries[0:3]
        l.append(entries[1])
        k.append(float(entries[23]) - float(entries[3]))
#        print l[i], k[i]
        i=i+1
        
#    print k
 
    rejects=[]
    rejectsk=[]
    rejectedind=[]
#    print 'Mean = ',mean, 'std = ',std
#    print 'max diff = ',max(k), min(k)

 
    flag=1
   
    
    while flag:
        flag=0
        mean,std=meanstdv(k)
        rejectedind=[]
        k2=[]
        l2=[]
        print 'Mean = ',mean, 'std = ',std
        print 'max diff = ',max(k), min(k)
        for i in range(len(k)):
            if  (k[i] > mean+4.*std or  k[i] < mean-4.*std) or \
               k[i] > 90. :
                flag=1
                print "rejecting ",l[i], k[i],i
                rejectedind.append(i)
                rejects.append(l[i])
                
            else:
                k2.append(k[i])
                l2.append(l[i])
        k=k2
        l=l2
        print  
        
#        else:
           # print "keeping: "+l[i], k[i]



    pylab.hist(k,100)
    #pylab.show()
    pylab.savefig('dist.png')


    print len(k), " left"
    oldobjs=open(sourcefile,'r').readlines()
    newfilename=sourcefile+".1"
    newfile=open(newfilename,'w')
    

    for line in oldobjs:
        entries=re.split('\s+',line)
        
        if entries[0] in rejects:
            print "rejecting: "+line
        else:
            newfile.write(line)

    newfile.close()
    print "wrote to "+newfilename


if __name__ == '__main__':
    
    file=sys.argv[1]
    source=sys.argv[2]
    doit(file,source)
