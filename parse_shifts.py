#!/usr/bin/env python

def parse(file,filters,columns):
    import re
    filters = re.split('\,',filters[:-1])

    print file, filters
    f = open(file).readlines()
    import string
    print filters 
    for line in f:
        if string.find(line,'SHIFTS') != -1:
            shifts = line
            res = re.split('\s+',shifts.replace(',',''))[2:-1]
            print res
        
            print shifts
            break

    raw = open(columns,'r').readlines()
    i = -1
    filen = columns.replace('.replace','')
    out = open(filen,'w')
    for line in raw:
        if string.find(line,'AB')!=-1:
            i += 1                                   
            if i < len(res):
                line = line.replace('REPLACE',res[i])
        print line
        out.write(line + '\n')
    out.close()

    print filen
    

if __name__ == '__main__':
    import sys, re
    parse(sys.argv[1],sys.argv[2],sys.argv[3])


