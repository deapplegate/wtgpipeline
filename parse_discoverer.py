import re
ls = open('dlist','r').readlines()
discoverers = {}
for l in ls:
    res = re.split('\s+',l[:-1])
    t = reduce(lambda x,y: x + y, res[1:])
    t = t.replace(' ','').replace('etal.','')
    res = re.split(',',t)
    print res
    for r in res:
        if r in discoverers: discoverers[r] += 1
        else: discoverers[r] = 1

list = []
for k in discoverers.keys():
    list.append([discoverers[k],k])

list.sort()
for l in list: print l
    
