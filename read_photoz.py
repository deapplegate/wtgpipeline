
def run(command,to_delete=[]):
    import os
    for file in to_delete: 
        os.system('rm ' + file)
    print command
    #raw_input()
    os.system(command)

from config_bonn import filters, cluster
import os
incat = os.environ['sne'] + '/0018.zsout' #'/tmp/zs.cat'
lphout = open(incat,'r').readlines()
ok = 1
i = 3
dict = {}
while ok:
    print lphout[i]
    line = lphout[i]
    i += 1
    if line[0] == '#':
        import re
        res = re.split('\:',line)
        print res
        if len(res) == 2:
            key = res[0].replace('#','').replace(' ','') 
            resvalue = re.split('\s+',res[1])
            if resvalue[0] == '': resvalue = resvalue[1:]
            if resvalue[-1] == '': resvalue = resvalue[:-1]
            dict[key] = resvalue
        elif lphout[i][0:3] == '# O': 
            ok = 0                
print dict
  
outputs = []
print lphout[i]
while lphout[i][0:2] == '# ': 

    i += 1
    res = re.split('\,',lphout[i].replace(' ','').replace('#','').replace('\n',''))
    print res
    outputs += res

print outputs

keys = []
for key in outputs:
    if key != '' and key != 'STRING_INPUT':
        if key[-2:] == '()':                                                                          
           if key == 'PDZ()':         
                intervals = []
                for i in range(len(dict['PROB_INTZ'])/2):  
                    keys.append(key[:-2] + '_' + dict['PROB_INTZ'][i] + '_' + dict['PROB_INTZ'][i+1])
           else:
                for filter in filters:             
                    keys.append(key[:-2] + '_' + filter)                 
        else: keys.append(key)

print keys

tempconf = '/tmp/photoz.conf'
conflist = open(tempconf,'w')
for key in keys:
    if key == 'ID' :
        conflist.write('COL_NAME = SeqNr\nCOL_TTYPE = LONG\nCOL_HTYPE = INT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')
    else:
        conflist.write('COL_NAME = ' + key + '\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n')
conflist.close()

import os
tempcat = '/tmp/zs.cat'
run('asctoldac -i ' + incat + ' -o ' + tempcat + ' -c ' + tempconf + ' -t STDTAB',[tempcat] )

input = reduce(lambda x,y: x + ' ' + y, keys)
run('ldacjoinkey -t OBJECTS -i /tmp/' + cluster + 'output.cat -p ' + tempcat + ' -o /tmp/' + cluster + 'final.cat -t STDTAB  -k ' + input)

for line in lphout:
    if line[0] != '#':
        res = re.split('\s+',line)
        tmp = {}  
        for i in range(len(res[1:])):
            tmp[keys[i]] = res[1+i]

        for key in keys:
            print key, tmp[key]
        #raw_input()
