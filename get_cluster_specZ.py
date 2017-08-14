#!/usr/bin/env python
import numpy,ldac
import sys 
import re, os
import pylab

def doit(file):

    f = ldac.openObjectFile(file)

    arr = numpy.zeros(151)
    for iz in f['Z']:
        #print iz
        n=int(iz*100.)
        if n>150:
            n=150
        if n < 0:
            n=0
        #print "filling ",n 
        arr[n]= arr[n]+1

    max = 0
    maxind=0
    for i in range(151):
        #print max , maxind,arr[i] 
        if arr[i]>max:
            max=arr[i]
            maxind=i
    print float(maxind)/100.


if __name__ == '__main__':
    
    file=sys.argv[1]

    doit(file)
