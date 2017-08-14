

#this queries the SDSS database for spectroscopic objects
#around a position ${ra}, ${dec}

#you can query both stars and galaxies with the table
#PhotoPrimary , see
#http://cas.sdss.org/dr7/en/help/browser/description.asp?n=PhotoObjAll&t=U

import os, utilities

#if [ ! -f CasJobs.config ]; then
#  ln -s ${HOME}/software/casjobs/CasJobs.config .
#fi

name = 'test'
ra = 18.87667 
dec = -0.86083 
radius = 10
os.system('rm ' + name + '_sdss_anja*.csv')
java = '/afs/slac/g/ki/software/java/jdk1.6.0_07/bin/java'
utilities.run(java + ' -jar casjobs.jar execute -t mydb/1 "drop table ' + name + '_sdss"')
utilities.run(java + ' -jar casjobs.jar run -t dr7collab \
"select top 1000 p.objID, \
p.ra, \
p.dec, \
n.distance, \
s.z, \
s.zErr, \
s.zConf, \
s.zWarning, \
s.specClass \
into mydb.' + name + '_sdss \
from fGetNearbyObjAllEq(' + str(ra) + ',' + str(dec) + ',' + str(radius) + ') n, Galaxy as p, SpecObjAll as s \
where p.objID = s.BestObjID \
and n.objID=p.objID"')
utilities.run(java + ' -jar casjobs.jar extract -b ' + name + '_sdss -type csv -d -force')
utilities.run(java + ' -jar casjobs.jar execute -t mydb/1 "drop table ' + name + '_sdss"')

#sed 's/\,/\ /g' ${name}_sdss_anja*.csv > tmp.dat
#awk '{if ($1!="#" && $1>0 && $1!="objID") print $0}' tmp.dat > ${name}_sdss.dat
