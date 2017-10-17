#! /usr/bin/env python
#adam-does# This code is an adaptation of do_photometry.py, which doesn't use lephare at all, but uses the properly calibrated photometry to get photoz's using the "bpz.py" package
#adam-prelims# export cluster=MACS1226+21 ; export BPZPATH='/nfs/slac/kipac/fs1/u/awright/InstallingSoftware_extension/bpz-1.99.3/' ; export sne=/nfs/slac/g/ki/ki04/pkelly ; export INSTRUMENT=SUBARU ; export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU ; export subdir=${SUBARUDIR};export subarudir=${SUBARUDIR} ; export bonn=/u/ki/awright/bonnpipeline/ ; export "PYTHONPATH=${PYTHONPATH}:${BPZPATH}"; export NUMERIX="numpy"
#adam-example# ipython -i -- adam_do_photometry.py $cluster detect=W-C-RC aptype=aper APER1
## python /nfs/slac/kipac/fs1/u/awright/InstallingSoftware_extension/bpz-1.99.3//bpz.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0.cat -COLUMNS /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/spec.APER1._aper.CWWSB_capak.list.cat.columns -MAG no -SPECTRA CWWSB_capak.list -PRIOR hdfn_SB -CHECK yes -PLOTS yes -VERBOSE no -ZMAX 4.0 -PLOTS yes -INTERP 8 -PROBS_LITE /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0.probs -OUTPUT /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0.bpz

#adam-note#  inputfile= /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.calibrated.cat
#adam-note#  outputfile= /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.APER1.1.CWWSB_capak.list.all.EVERY.cat
#These environment variables should be set before running this code:
#	export BPZPATH=/nfs/slac/kipac/fs1/u/awright/InstallingSoftware_extension/bpz-1.99.3/
#	export "PYTHONPATH=${PYTHONPATH}:${BPZPATH}"; export NUMERIX="numpy"
#	export sne=/nfs/slac/g/ki/ki04/pkelly
#	export INSTRUMENT=SUBARU ; export SUBARUDIR=/nfs/slac/g/ki/ki18/anja/SUBARU ; export subdir=${SUBARUDIR};export subarudir=${SUBARUDIR}
#	export bonn=/u/ki/awright/bonnpipeline/

########import make_lephare_cats
import adam_do_multiple_photoz
import os, re, sys, string, numpy
import astropy.io.fits as pyfits
#adam-old# os.environ['BPZPATH']='/nfs/slac/g/ki/ki04/pkelly/bpz-1.99.2/'

subarudir = os.environ['subdir']
cluster = sys.argv[1]
#adam-tmp# spec = False
spec = True #adam-tmp#
train_first = False  ; test_zps = False ; short = False ; only_type=False
magtype = 'APER1'
AP_TYPE = ''
type = 'all'
SPECTRA='CWWSB_capak.list'
#SPECTRA options are: CWWSB_capak.list/CWWSB4.list/ZEBRA.list/CWWSB_capak_uz.list/CWWSB_capak_ub.list/CWWSB_capak_u.list/CWWSB4_txitxo.list

FILTER_WITH_LIST=None
if len(sys.argv) > 2:
    for s in sys.argv:
        if s == 'spec':
            type = 'spec'
            spec = True
        if s == 'rand':
            type = 'rand'
        if s == 'train':
            train_first = True
        if s == 'ISO':
            magtype = 'ISO'
        if s == 'APER1':
            magtype = 'APER1'
        if s == 'short':
            short = True
        if s == 'APER':
            magtype = 'APER'
        if s == 'only_type':
            only_type=True
        if string.find(s,'flist') != -1:
            rs = re.split('=',s)
            FILTER_WITH_LIST=rs[1]
        if s == 'zp':
            test_zps = True
        if string.find(s,'detect') != -1:
            rs = re.split('=',s)
            DETECT_FILTER=rs[1]
        if string.find(s,'spectra') != -1:
            rs = re.split('=',s)
            SPECTRA=rs[1]
        if string.find(s,'aptype') != -1:
            rs = re.split('=',s)
            AP_TYPE = '_' + rs[1]

print ' FILTER_WITH_LIST=',FILTER_WITH_LIST , ' AP_TYPE=',AP_TYPE , ' DETECT_FILTER=',DETECT_FILTER , ' magtype=',magtype , ' type=',type , ' only_type=',only_type , ' spec=' , spec,' train_first=',train_first

''' photoz parameters '''
photdir = subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + AP_TYPE + '/'
calib_type = 'slr'
picks = None #[11757]
ID = 'SeqNr' #adam-old# ID = 'PatID'
magflux = 'FLUX'

inputcat = photdir + cluster + '.calibrated.cat'
inputcat_alter_ldac = photdir + cluster + '.calibrated.alter.cat'

print ' SPECTRA=',SPECTRA , ' inputcat=',inputcat , ' inputcat_alter_ldac=',inputcat_alter_ldac

## this just basically puts SeqNr in 1st column, but I'll keep it here so that I have an entirely different catalog to mess with when running bpz
def add_dummy_ifilter(catalog, outputfile):
    ''' This puts SeqNr in the first column. And it drops the "APER-" columns while keeping the "APER1-" columns
	Note: This function in adam_do_multiple_photoz also adds "new Subaru W-S-I+ filter", which is no longer necessary as far as I know, but I'll have to wait until I have a cluster that has data from that filter in order to be certain that it isn't treated differently '''

    cols = []
    tables = pyfits.open(catalog)['OBJECTS']
    
    for col in ['SeqNr']:
        cols.append(pyfits.Column(name=col, format = 'J', array = tables.data.field(col)))

    for column in tables.columns:           
        if column.name=='SeqNr':continue
        if "APER-" in column.name:
		print outputfile+" won't contain this column: ",column.name
		continue
        cols.append(column)
    print 'add_dummy_ifilter| len(cols)=',len(cols)
    hdu = pyfits.PrimaryHDU()
    #old#hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
    hduSTDTAB = pyfits.BinTableHDU.from_columns(cols)
    hdulist = pyfits.HDUList([hdu,hduSTDTAB])
    #old#hdulist[1].header['EXTNAME']='OBJECTS'
    hdulist[1].header['EXTNAME']='OBJECTS'
    print 'add_dummy_ifilter| outputfile=',outputfile
    hdulist.writeto(outputfile,overwrite=True)

print "running: add_dummy_ifilter(inputcat,inputcat_alter_ldac)"
add_dummy_ifilter(inputcat,inputcat_alter_ldac)

filterlist = adam_do_multiple_photoz.get_filters(inputcat_alter_ldac,'OBJECTS',SPECTRA=SPECTRA)
print ' filterlist=',filterlist , ' len(filterlist)=',len(filterlist)

#adam-SHNT# will have to adjust this if there are later clusters with available spec-z's
## make the columns bpz input file
#obj_table=pyfits.open(inputcat_alter_ldac)['OBJECTS']
inputcat_alter_ascii= photdir + cluster + '.bpz_input.txt'
columns_fl= photdir + cluster + '.bpz.columns'
columns_fo= open(columns_fl,'w')
columns_num=2
ascii_cat_keys=["SeqNr"]
M_0_filt="W-C-RC" #this is the filter to use for "M_0", the mag most comparable to SDSS/2MASS/etc. deepest filter
M_0_key=None #this gets set in the loop
for filt in filterlist:
	filt_col=[filt,'%i,%i' % (columns_num,1+columns_num),'AB','0.02','0.0\n']
	columns_fo.write('\t'.join(filt_col))
	ascii_cat_keys.append("FLUX_APER1-"+filt+"_bpz")
	ascii_cat_keys.append("FLUXERR_APER1-"+filt+"_bpz")
	columns_num+=2
	if M_0_filt in filt:
		M_0_key=filt

if M_0_key==None:
	raise Exception("the filter %s used for M_0 didn't show up in filterlist" % (M_0_filt))

columns_fo.write('\t'.join(['ID','1\n']))
columns_fo.write('\t'.join(['M_0',str(columns_num)+'\n']))
ascii_cat_keys.append("MAG_APER1-"+M_0_key)
if spec:
	columns_num+=1
	columns_fo.write('\t'.join(['Z_S',str(columns_num)+'\n']))
	#ascii_cat_keys.append("Z_S")
columns_fo.close()


command="ldactoasc -i %s -t OBJECTS -s -b -k %s > %s" % (inputcat_alter_ldac,' '.join(ascii_cat_keys),inputcat_alter_ascii)
print "command=",command
ooo=os.system(command)
if ooo!=0: raise Exception("the line os.system(ldactoasc...) failed")

if spec:
	#adam-SHNT# including Z_S in the bpz input ascii file
	spec_file="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/Zspecs_for_bpz.txt"
	##outtable.write("%s/Zspecs_for_bpz.txt" % (bpz_path),format="ascii.commented_header")
	#first call is SeqNr and 2nd col is Z, so loop over other file's SeqNr's, where it matches an SeqNr from this file, include the specz, where it doesn't, put in a +99

########''' retrieve SDSS spectra '''
########
########''' make spectra file '''
#########
########''' make the catalogs '''

########filterlist_short = filter(lambda x: string.find(x,'10_2-2') == -1 and string.find(x,'10_1-2') == -1, filterlist)
########print ' filterlist_short=',filterlist_short
########''' TRAINING ONLY ON u-band '''
########train_filters = ['WHT-0-1-U','MEGAPRIME-10_2-1-u','MEGAPRIME-0-1-u','SUBARU-10_2-1-W-J-U','SUBARU-10_1-1-W-J-U']
########train_filters += ['SUBARU-10_1-1-W-J-B','SUBARU-10_2-1-W-J-B','SUBARU-9-4-W-J-B','SUBARU-9-2-W-J-B']

########overlap = False
########for filt1 in filterlist:
########    for filt2 in train_filters:
########	if filt1==filt2: overlap = True
########print ' overlap=',overlap

########speccat = photdir + cluster + 'spec.cat'
########from glob import glob
########if not glob(speccat):
########    os.system('cp ' +  subarudir + '/' + cluster + '/PHOTOMETRY_' + DETECT_FILTER + '/' + cluster + 'spec.cat ' + speccat)
########outspeccat = photdir + 'spec.' + magtype + '.' + AP_TYPE+ '.' + SPECTRA + '.cat'
########outfullcat = photdir + 'all.' + magtype + SPECTRA + '.cat'
########make_lephare_cats.doit(cluster,DETECT_FILTER,filterlist, inputcat_alter_ldac,speccat,outspeccat,outfullcat,spec,'','',magtype=magtype,randsample=False,magflux=magflux,inputcat_zlist=None)

short = True
print 'inputs for adam_do_multiple_photoz.do_bpz: cluster=',cluster , ' DETECT_FILTER=',DETECT_FILTER , ' AP_TYPE=',AP_TYPE , ' filterlist=',filterlist ,' inputcat_alter_ascii=',inputcat_alter_ascii, ' inputcat_alter_ldac=',inputcat_alter_ldac , ' calib_type=',calib_type , ' spec=',spec , ' SPECTRA=',SPECTRA , ' picks=',picks , ' magtype=',magtype , ' magflux=',magflux , ' short=',short , ' ID=',ID , ' only_type=',only_type, 'inputcolumns=', columns_fl
print 'inputs for adam_do_multiple_photoz.do_bpz: '
print '\tcluster: '+cluster 
print '\tDETECT_FILTER: '+DETECT_FILTER 
print '\tAP_TYPE: '+AP_TYPE 
print '\tfilterlist: ',filterlist 
print '\tinputcat_alter_ascii: ',inputcat_alter_ascii 
print '\tinputcat_alter_ldac: ',inputcat_alter_ldac 
print '\tcalib_type: ',calib_type 
print '\tspec: ',spec 
print '\tSPECTRA: ',SPECTRA 
print '\tpicks: ',picks 
print '\tmagtype: ',magtype 
print '\tmagflux: ',magflux 
print '\tshort: ',short 
print '\tID: ',ID 
print '\tonly_type: ',only_type 
print '\tinputcolumns: ',columns_fl 

#previous call: python  /nfs/slac/g/ki/ki04/pkelly/bpz-1.99.2//bpz.py /nfs/slac/g/ki/ki18/anja/SUBARU//MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.bpz_input.txt -COLUMNS /nfs/slac/g/ki/ki18/anja/SUBARU//MACS1226+21/PHOTOMETRY_W-C-RC_aper/MACS1226+21.bpz.columns  -MAG no  -SPECTRA CWWSB_capak.list  -PRIOR hdfn_SB  -CHECK yes  -PLOTS yes  -VERBOSE no  -ZMAX 4.0  -INTERP 8  -PROBS_LITE /nfs/slac/g/ki/ki18/anja/SUBARU//MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpz-APER1.CWWSB_capak.probs.list  -OUTPUT /nfs/slac/g/ki/ki18/anja/SUBARU//MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpz-APER1.CWWSB_capak.bpz.list 2>&1 | tee -a OUT-bpz.log

#adam-old# adam_do_multiple_photoz.do_bpz(cluster,DETECT_FILTER, AP_TYPE, filterlist,inputcat_alter_ldac, calib_type,spec,SPECTRA, picks,magtype=magtype,randsample=False,magflux=magflux,short=short,ID=ID,only_type=only_type)
try:
	adam_do_multiple_photoz.do_bpz(cluster,DETECT_FILTER, AP_TYPE, filterlist,inputcat_alter_ascii,inputcat_alter_ldac, calib_type,spec,SPECTRA, picks,magtype=magtype,randsample=False,magflux=magflux,short=short,ID=ID,only_type=only_type,inputcolumns=columns_fl)
except:
	ns=globals() #adam-tmp
	ns.update(adam_do_multiple_photoz.ns_dmp) #adam-tmp
	raise
#########import cutout_bpz
#########cutout_bpz.run(cluster)
#########os.system('python cutout_bpz.py ' + cluster + ' spec')
########''' now make the cutout images '''
########''' python cutout_bpz.py '''
print 'TO SAVE OUTPUT ZP fits: grep -A 12 "PHOTOMETRIC CALIBRATION TESTS" OUT-bpz_lasttime.log > adam_bpz_fit_ZPs-without_specz.log'
print 'grep -A 12 "PHOTOMETRIC CALIBRATION TESTS" OUT-bpz_lasttime.log > adam_bpz_fit_ZPs-without_specz.log'



#adam-SHNT# get these working again!
#python $BPZPATH/bpzfinalize.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0
print "for more info, run this: python $BPZPATH/bpzfinalize.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0"

### gives us: Saving  /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0_bpz.cat
#Includes calculation of modified chisq (chisq2) plus different formatting #Important: Check your results including SED fits and P(z)
# python $BPZPATH/plots/webpage.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0 i0-63 -DIR /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/bpz_html_sex2mag
print "for more info, run this: python $BPZPATH/plots/webpage.py /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/all_bpzAPER1CWWSB_capak.list1_0 i0-63 -DIR /nfs/slac/g/ki/ki18/anja/SUBARU/MACS1226+21/PHOTOMETRY_W-C-RC_aper/bpz_html_sex2mag"
