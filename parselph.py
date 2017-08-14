import sys, os

os.system('cp lph_sn sntmp')

LIB = 'PEGASE2' #'BC03'
DIR = 'PEGASE2' #'BC03_CHAB'
kind = 'peg'

if  False:
    os.system('filter -c $LEPHAREDIR/config/me.para')
    os.system('sedtolib -t G -c $LEPHAREDIR/config/me.para -GAL_SED $LEPHAREDIR/sed/GAL/' + DIR + '/' + LIB + '_MOD.list -GAL_LIB LIB_' + LIB)
    os.system('mag_gal -t G -c $LEPHAREDIR/config/me.para -GAL_LIB_IN LIB_' + LIB + ' -GAL_LIB_OUT ' + LIB + '_GAL')

sndo = 1
ERR_FACTOR = 0.5
while sndo > 0: 
    sndo = 0
    ERR_FACTOR += 0.5 
    command = 'zphota -c $LEPHAREDIR/config/me.para  -CAT_IN $util/sntmp -CAT_OUT $util/lph_zs -ZPHOTLIB ' + LIB + '_GAL -ERR_FACTOR ' + str(ERR_FACTOR)
    print command
    import os
    os.system(command)
    
    f = open('lph_sn','r').readlines()
    sns = {}
    for line in f:
        import re
        res = re.split('\s+',line[:-1])
        print res
        if res[-1] == '': res = res[:-1]
        print res[0], res[-1]
        sns[float(res[0])] = {'sn':res[-1], 'line':line}
    print sns
    
    f = open('lph_zs','r').readlines()
    sntmp = open('sntmp','w')
    key_start = False
    keys ={} 
    for line in f:
        import string
        if key_start:
            import re
            res = re.split(',',line[1:])
            for r in res:
                res2 = re.split('\s+',r)
                print res2
                if len(res2) > 2:
                    keys[res2[2]] = res2[1]
        if string.find(line,'Output format') != -1:
            key_start = True
        if string.find(line,'########') != -1:
            key_start = False 
        print keys
        if string.find(line,'#') == -1:
            res = re.split('\s+',line)
            import anydbm
            sn = sns[float(res[1])]['sn']
            gh = {} 
            db = anydbm.open(sn)
            
            for j in range(len(res)):
                if keys.has_key(str(j)):
                    gh[keys[str(j)]] = str(res[j])
                    print gh[keys[str(j)]], kind + '_' + keys[str(j)]
                    print sn, keys[str(j)], str(res[j])
            print gh
            if float(gh['MASS_MED']) != -99:
                for key in gh.keys():
                    db[kind + '_' + key] = gh[key]
            else:
                sndo += 1
                sntmp.write(sns[float(res[1])]['line'])
            
    sntmp.close()
                    
