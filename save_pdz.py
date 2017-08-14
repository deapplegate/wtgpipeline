#!/usr/bin/env python
import numpy
import sys 
import re, os
import pylab



#
#
# need to get the ids from lph inputfile...
#
#

def doit(pdzfile,lphoutput,outfile):


    lphfile = open(lphoutput,'r')
    idlist=[]
    specs=[]
    for line in lphfile.readlines():
        if line[0] == "#":
        #    print "skipping ",line
            continue
        
        entries=re.split('\s+',line)
        #     print entries
        idlist.append(entries[1])
        last=len(entries)
        specs.append(entries[last-2])
        
        #    print len(specs)
    z0=0
    zf=4
    dz=0.02

    flist=open(pdzfile,'r').readlines()
    outfile=open(outfile,'w')

    k=0
    for line in flist:
        thisset={'z':[], 'p':[]}
        linelist=re.split('\s+',line)
        flag=0
        # print linelist, len(linelist)
        for i in range(len(linelist)):
            # print z0+(i)*dz, linelist[i]
            if linelist[i]=='':
                continue
            if flag==0 and float(linelist[i])>0:
                # print "Entering 1"
                if linelist[i-1]!='':
                    thisset['z'].append(z0+(i-1)*dz)
                    thisset['p'].append(linelist[i-1])
                    #print z0+(i-1)*dz, linelist[i-1]

                thisset['z'].append(z0+i*dz)
                thisset['p'].append(linelist[i])
              
                # print z0+(i)*dz, linelist[i]
                
                flag=1
            elif flag!=0 and float(linelist[i])>0:
                # print "Entering 2"
                thisset['z'].append(z0+i*dz)
                thisset['p'].append(linelist[i])
                # print z0+(i)*dz, linelist[i]
                
            elif flag!=0 and float(linelist[i])==0: 
                # print "Entering 3"
                thisset['z'].append(z0+i*dz)
                thisset['p'].append(linelist[i])
                # print z0+(i)*dz, linelist[i]
                
                flag=0

        #thisset['z'].append(zf)
        #thisset['p'].append(0)
        # print k
        # print "ID=",idlist[k]
        # print "spec=",specs[k]
        outfile.write(str(idlist[k])+":"+str(specs[k])+" ")
        k+=1
        # print thisset['z']
        # print thisset['p']
            
            
        pylab.plot( thisset['z'],  thisset['p'] )
#        pylab.show()
        for j in range(len(thisset['z'])):
            outfile.write(str(thisset['z'][j])+":"+str(thisset['p'][j])+" ")
                
        outfile.write("\n")
    outfile.close()

        
     
if __name__ == '__main__':
    
    pdzfile=sys.argv[1]
    lphoutput=sys.argv[2]
    outfile=sys.argv[3]
    doit(pdzfile,lphoutput,outfile)
