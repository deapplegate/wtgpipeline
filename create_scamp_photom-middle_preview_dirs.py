#! /usr/bin/env python
#adam-example# ./create_scamp_photom-middle_combine_dirs.py RXJ2129
import sys,os,re
from glob import glob
def get_path_supa_chip_ending(im):                                                                                                                                                                       
        '''example: im='/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE/SUPA0128347_10OCFI.fits'
        get_path_supa_chip_ending(im)= ('/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE', 'SUPA0128347', '10', 'OCFI')'''
        path=os.path.dirname(im)
        basename=os.path.basename(im)
        name_match=re.match("SUPA([0-9]*)_([0-9]{1,2})([A-Z]*).fits",basename)
        supa="SUPA"+name_match.group(1)
        chip=name_match.group(2)
        ending=name_match.group(3)
        return path,supa,chip,ending

# for each path, I want to know if there are multiple endings for each supa, and what they are
def get_supa_chip_endings(ims):
        '''example: im='/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE/SUPA0128347_10OCFI.fits'
        get_path_supa_chip_ending(im)= ('/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/W-S-Z+/SCIENCE', 'SUPA0128347', '10', 'OCFI')'''
	paths={}
	endings={}
	for im in ims:
		path=os.path.dirname(im)
		basename=os.path.basename(im)
		basename=basename.split('.')[0]
		name_match=re.match("SUPA([0-9]*)_([0-9]{1,2})([A-Z]*)",basename)
		supa="SUPA"+name_match.group(1)
		chip=name_match.group(2)
		ending=name_match.group(3)
		if not paths.has_key(path):
			paths[path]={}
		if not paths[path].has_key(supa):
			paths[path][supa]={}
		if not paths[path][supa].has_key(ending):
			paths[path][supa][ending]=[]
		paths[path][supa][ending].append(chip)
		if not ending in endings.keys():
			endings[ending]=0
		endings[ending]+=1
        return paths,endings


from my_cluster_params import ic_cldata,clusters_refcats
data_root=os.environ['SUBARUDIR']

cluster=sys.argv[-1]

newdir="/gpfs/slac/kipac/fs1/u/awright/SUBARU/"+cluster+"/"
olddir="/nfs/slac/g/ki/ki05/anja/SUBARU/"+cluster+"/"
astrom_filt_new="W-J-B"
astrom_filt_old="W-J-B"
if cluster=='MACS0429-02' or cluster=='Zw2089':
	astrom_filt_old="W-J-V"

## combine the astrom directories first:
astrom_newdir_candidates=glob(newdir+"/"+astrom_filt_new+"/SCIENCE/astrom_photom_scamp_*/")
if len(astrom_newdir_candidates)==1:
	astrom_newdir=astrom_newdir_candidates[0]
	print ' astrom_newdir=',astrom_newdir
else:
	print ' astrom_newdir_candidates=',astrom_newdir_candidates
	if cluster=='MACS0429-02':
		astrom_newdir=newdir+"/"+astrom_filt_new+"/SCIENCE/astrom_photom_scamp_PANSTARRS/"
	else:
		raise Exception('ambiguity in which astrom_photom_scamp_.../ directory to use')

astrom_olddir_candidates=glob(olddir+"/"+astrom_filt_old+"/SCIENCE/astrom_photom_scamp_*/")
if len(astrom_olddir_candidates)==0:
	print ' astrom_filt_old=',astrom_filt_old
	raise Exception('wrong filter to use to find astrom_photom_scamp_.../ directory in OLD DIR')
elif len(astrom_olddir_candidates)==1:
	astrom_olddir=astrom_olddir_candidates[0]
	print ' astrom_olddir=',astrom_olddir
else:
	print ' astrom_olddir_candidates=',astrom_olddir_candidates
	raise Exception('ambiguity in which astrom_photom_scamp_.../ directory to use')

print "ln -s "+astrom_olddir+"/cat_photom/SUPA* "+astrom_newdir+"/cat_photom/"
print "ln -s "+astrom_olddir+"/cat/SUPA*.ahead "+astrom_newdir+"/cat/"
print "ln -s "+astrom_olddir+"/headers/SUPA* "+astrom_newdir+"/headers/"

filters=["W-J-B","W-J-V","W-C-RC","W-S-I+","W-C-IC","W-S-Z+"]
sciendings={'new':{},'old':{}}
catendings={'new':{},'old':{}}

catfls=glob(astrom_olddir+'cat_photom/SUPA*.ldac')
paths,endings2=get_supa_chip_endings(catfls)
print '\n######## '+cluster+' #########'
for filt in filters:

	filtstr="    "+filt+": "
	if os.path.isdir(olddir+"/"+filt+"/"):
		oldppruns=glob(olddir+"/"+filt+"_20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]")
		oldpprun=' '.join([ pprundirstr.rsplit('/')[-1] for pprundirstr in oldppruns])
		filtstr=""+filtstr+" : SCIENCE in OLD"
		old_sci_dir=olddir+filt+"/SCIENCE"
		sciims=glob(old_sci_dir+"/SUPA*.fits")
		sciims=filter( lambda x: not x.endswith('sub.fits') ,sciims)
		paths,endings1=get_supa_chip_endings(sciims)
		sciendings['old'][filt]=endings1
		supas=paths[old_sci_dir].keys()
		catfls=[]
		for supa in supas:
			catfls+=glob(astrom_olddir+'cat_photom/'+supa+'*.ldac')
		paths,endings2=get_supa_chip_endings(catfls)
		catendings['old'][filt]=endings2
		print'old',filt,endings1,endings2,oldpprun
	if os.path.isdir(newdir+"/"+filt+"/"):
		newppruns=glob(newdir+"/"+filt+"_20[0-9][0-9]-[0-9][0-9]-[0-9][0-9]")
		newpprun=' '.join([ pprundirstr.rsplit('/')[-1] for pprundirstr in newppruns])
		filtstr=""+filtstr+" : SCIENCE in NEW"
		new_sci_dir=newdir+filt+"/SCIENCE"
		sciims=glob(new_sci_dir+"/SUPA*I.fits")
		sciims=filter( lambda x: not x.endswith('sub.fits') ,sciims)
		paths,endings1=get_supa_chip_endings(sciims)
		sciendings['new'][filt]=endings1
		supas=paths[new_sci_dir].keys()
		catfls=[]
		for supa in supas:
			catfls+=glob(astrom_newdir+'cat_photom/'+supa+'*.ldac')
		paths,endings2=get_supa_chip_endings(catfls)
		catendings['new'][filt]=endings2
		print'new',filt,endings1,endings2,newpprun
	oldcalibs=glob(olddir+"/"+filt+"*CALIB/")
	newcalibs=glob(newdir+"/"+filt+"*CALIB/")

	if len(oldcalibs)==1:
		calibdirstr='/'.join(oldcalibs)
		oldcalib=' '.join([ x for x in calibdirstr.rsplit('/') if x.endswith('_CALIB')])
		filtstr=""+filtstr+" : CALIB in OLD (%s)" % (oldcalib)
	if len(newcalibs)==1:
		calibdirstr='/'.join(newcalibs)
		newcalib=' '.join([ x for x in calibdirstr.rsplit('/') if x.endswith('_CALIB')])
		filtstr=""+filtstr+" : CALIB in NEW (%s)" % (newcalib)
	print filtstr+'\n'


