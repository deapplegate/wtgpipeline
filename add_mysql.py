#!/usr/bin/env python

def add_to_db(dict):

    CLUSTER = dict['CLUSTER']

    db2,c = connect_except()
    
    command = "CREATE TABLE IF NOT EXISTS zpshifts_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))"
    #print command
    #c.execute("DROP TABLE IF EXISTS illumination_db")
    #c.execute(command)

    from copy import copy
    floatvars = {}  
    stringvars = {}
    #copy array but exclude lists                                                   
    import string
    letters = string.ascii_lowercase + string.ascii_uppercase.replace('E','') + '_' + '-' + ','
    for ele in dict.keys():
        type = 'float'
        for l in letters:
            if string.find(str(dict[ele]),l) != -1: 
                type = 'string'
        if type == 'float':  
            floatvars[ele] = str(float(dict[ele])) 
        elif type == 'string':
            stringvars[ele] = dict[ele] 
                                                                                                                                                                                                           
    # make database if it doesn't exist
    print 'floatvars', floatvars
    print 'stringvars', stringvars
    
    for column in stringvars: 
        try:
            command = 'ALTER TABLE zpshifts_db ADD ' + column + ' varchar(240)'
            c.execute(command)  
        except: nope = 1 
    
    for column in floatvars: 
        try:
            command = 'ALTER TABLE zpshifts_db ADD ' + column + ' float(30)'
            c.execute(command)  
        except: nope = 1 

    # insert new observation 

    c.execute("SELECT CLUSTER from zpshifts_db where CLUSTER='" + CLUSTER + "'")
    results = c.fetchall() 
    print results
    if len(results) > 0:
        print 'already added'
    else:
        command = "INSERT INTO zpshifts_db (CLUSTER) VALUES ('" + CLUSTER + "')"
        print command
        c.execute(command) 

    import commands

     
    vals = ''
    for key in stringvars.keys():
        print key, stringvars[key]
        vals += ' ' + key + "='" + str(stringvars[key]) + "',"

    for key in floatvars.keys():
        print key, floatvars[key]
        vals += ' ' + key + "='" + floatvars[key] + "',"
    vals = vals[:-1]

    command = "UPDATE zpshifts_db set " + vals + " WHERE CLUSTER='" + CLUSTER + "'" 
    print command
    c.execute(command)
        
    print vals
        
    db2.close()




if __name__ == '__main__':
    import sys, re
    args = sys.argv[:1]
    dict = {}
    for arg in args: 
        key,value = re.split('=',arg)
        dict[key] = value
    
        save_exposure(dict)
