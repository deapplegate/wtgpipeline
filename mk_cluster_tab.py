import MySQLdb, sys, os, re, time, utilities, astropy.io.fits as pyfits                                                                                                                          
from copy import copy
db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-sr01')
c = db2.cursor()

command = "CREATE TABLE IF NOT EXISTS clusters_db ( id MEDIUMINT NOT NULL AUTO_INCREMENT, PRIMARY KEY (id))"
print command
#c.execute("DROP TABLE IF EXISTS clusters_db")
c.execute(command)
command = "alter table clusters_db add column objname varchar(100)" 
#c.execute(command)
command = "alter table clusters_db add column info varchar(700)" 
#c.execute(command)

import re
f = open('cluster_cat_filters.dat','r').readlines()
for l in f:
    print l
    res = re.split('\s+',l[:-1])
    print res
    command = 'insert into clusters_db (objname,info) values ("' + res[0] + '","' + l[:-1] + '")'

    command = 'update clusters_db set info="' + l[:-1] + '" where objname="' + res[0] + '"'
    print command
    c.execute(command)
    
