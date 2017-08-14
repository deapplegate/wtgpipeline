import MySQL, sys, os, re

db2 = MySQLdb.connect(db='subaru', user='weaklensing', passwd='darkmatter', host='ki-rh8')
c = db2.cursor()
c.execute(command)
