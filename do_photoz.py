class file_iter:
    def __init__(self,name):
        self.name = name
        self.suffix = 1
        self.file = self.name + str(self.suffix) 
    def next(self):
        self.suffix += 1    
        self.file = self.name + str(self.suffix) 
        return self.file
    def __iter__(self):
        self.file = self.name + str(self.suffix) 

def match_list(line,dict_list):
    dict = {} 
    res = re.split('\s+',line)
    if res[0] == '':
        res = res[1:]
    
    #print res, dict_list
    #print len(res), len(dict_list)
    for i in range(len(dict_list)):
        #print dict_list[i], res[i]
        dict[dict_list[i]] = res[i]
    return dict

def run(command,to_delete=[]):
    import os
    for file in to_delete: 
        os.system('rm ' + file)
    print command
    #raw_input()
    os.system(command)

def special_objects():
    positions = [[340.82517,-9.59653,'faint_arc'],[340.8501,-9.58396,'main_knot_bright'],[340.84933,-9.58306,'lower_knot_bright'],[340.84933,-9.58306,'upper_knot_bright']]
    tempfile = '/tmp/tmppos'
    tempcat = '/tmp/tmpcat.cat'
    tempconf = '/tmp/tmpconf.conf'  
    tmp = open(tempfile,'w')
    tmp_ind = 0
    for ps in positions: 
        tmp_ind += 1
        tmp.write(str(tmp_ind) + ' ' + str(ps[0]) + ' ' + str(ps[1]) + '\n')
    tmp.close() 

    tf = open(tempconf,'w')
    tf.write(\
        'COL_NAME = SeqNr\nCOL_TTYPE = LONG\nCOL_HTYPE = INT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n'\
        + 'COL_NAME = ALPHA_J2000\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n'\
        + 'COL_NAME = DELTA_J2000\nCOL_TTYPE = DOUBLE\nCOL_HTYPE = FLOAT\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 1\n#\n'\
        )

        #+ 'COL_NAME = OBJECT\nCOL_TTYPE = STRING\nCOL_HTYPE = STRING\nCOL_COMM = ""\nCOL_UNIT = ""\nCOL_DEPTH = 128\n'\
    tf.close() 

    run('asctoldac -i ' + tempfile + ' -o ' + tempcat + ' -c ' + tempconf + ' -t STDTAB',[tempcat] )

    return tempcat
    
def convert_spectra(specfile):
    run("ldacrentab -i " + specfile.file + " -t OBJECTS STDTAB FIELDS NULL -o " + specfile.next(),[specfile.file])
    run("ldacrenkey -i " + specfile.file  + " -t STDTAB -k Ra ALPHA_J2000 Dec DELTA_J2000 Z z -o " + specfile.next(),[specfile.file])
    run("ldaccalc -i " + specfile.file + " -t STDTAB -c '(Nr);'  -k LONG -n SeqNr '' -o " + specfile.next(),[specfile.file] )
    return specfile

from config_bonn import cluster, tag, arc, magnitude, filters, spectra,area 
import sys, os, re

spec = 'yes'
arc_calc = 'no'
everything = 'no'

caltable = '/tmp/' + cluster + 'output.cat' #sys.argv[1]
caltablearc = '/tmp/' + cluster + 'output.arc.cat' #sys.argv[1]
#spectra = '/tmp/0911.cat' # 'M2243_spectra.cat' #sys.argv[2]
ppid = str(os.getppid())
calrename1 = '/tmp/cal1' # 
#filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']

if spec == 'yes':
    ''' rename tables '''
    ##os.system("ldacrentab -i " + caltable + " -t OBJECTS STDTAB FIELDS NULL -o " + calrename1)
    
    specfile = file_iter('/tmp/' + cluster + 'spec')
    os.system('cp ' + spectra + ' ' + specfile.file)
    specfile = convert_spectra(specfile) 
   
    print spectra

    matchspec = '/tmp/' + cluster + 'matchspec'
    matchspecfilt_first = '/tmp/' + cluster + 'matchspec.first.filt'
    matchspecfilt = '/tmp/' + cluster + 'matchspec.filt'
    print "match_neighbor.sh " + matchspec + " STDTAB " + specfile.file + " spec " +  caltable + " data "
    run("match_neighbor.sh " + matchspec + " STDTAB " + specfile.file + " spec " +  caltable + " data ", [matchspec])
    #print  "ldacfilter -i " + matchspec + " -c '((z_spec != 0) AND (SeqNr_data != 0));' -t STDTAB -o " + matchspecfilt
    run("ldacfilter -i " + matchspec + " -c '((z_spec != 0) AND (SeqNr_data != 0));' -t STDTAB -o " + matchspecfilt_first ,[matchspecfilt_first])

    listcond = []                                                                                              
    for filter in filters:
        listcond.append('Flag_'+filter + "_data = 0)")
        listcond.append('IMAFLAGS_ISO_'+filter + "_data = 0)")
        #listcond.append('BackGr_'+filter + " > 0.00000001)")
    filt= '(' + reduce(lambda x,y: '(' + x + '  AND (' + y + ')',listcond)
    print filt

    command = 'ldacfilter -i ' + matchspecfilt_first + ' -t STDTAB -o ' + matchspecfilt + ' -c "' + filt + ';" '
    print command
    run(command,[matchspecfilt])

    #run("ldacfilter -i " + matchspecfilt_first + " -c '((N_00 = 0) AND (N_01 = 1));' -t STDTAB -o " + matchspecfilt ,[matchspecfilt])
    #####command="ldacfilter -i " + outputtable + " -c '(OldSeqNr != 0);' -t STDTAB -o " + outputtablefilt 
    
    #specialobjs = special_objects()
    #matchobj = '/tmp/matchobj'
    matchobjfilt = '/tmp/' + cluster + 'matchobj.filt'
    #run("match.sh " + matchobj + " STDTAB " + specialobjs + " obj " +  caltable + " data ", [matchobj])
    #run("ldacfilter -i " + matchobj + " -c '((ALPHA_J2000_obj != 0) AND (SeqNr_data != 0));' -t STDTAB -o " + matchobjfilt, [matchobjfilt])
    
    #seqnrs = [87657,91866,91073,92484]
    #conditionals = ['SeqNr=' + str(x) + ')' for x in seqnrs] 
    #filt= '(' + reduce(lambda x,y: '(' + x + '  OR (' + y + ')',conditionals)
    #matchobjfilt = '/tmp/matchobj.filt'
    #run('ldacfilter -i ' + caltablearc + ' -t STDTAB -o ' + matchobjfilt + ' -c "' + filt + ';" ')

''' make list of parameters to read out to photoz input file '''
mag_name = 'Mag_'   
magerr_name = 'MAGERR_APER1'
dict_list = []
dict_list_obj = []
dict_list_nomat = []
print_list = []
print_list_obj = []
print_list_nomat = []
for filter in filters:
    dict_list.append(mag_name + filter + '_data')
    dict_list.append(magerr_name + '_' + filter + '_data')
    print_list.append([mag_name + filter + '_data', magerr_name + '_' + filter + '_data'])
   
mag_name = 'MAG_SPEC_'   
magerr_name = 'MAGERR_SPEC'
for filter in filters:
    dict_list_obj.append(mag_name + filter )
    dict_list_obj.append(magerr_name + '_' + filter )
    print_list_obj.append([mag_name + filter , magerr_name + '_' + filter ])

mag_name = 'Mag_'   
magerr_name = 'MAGERR_APER2'
for filter in filters:
    dict_list_nomat.append(mag_name + filter )
    dict_list_nomat.append(magerr_name + '_' + filter )
    dict_list_nomat.append('Thresh_' + filter )
    #dict_list_nomat.append('FLUX_AUTO_' + filter )
    dict_list_nomat.append('Flag_' + filter )
    dict_list_nomat.append('BackGr_' + filter )
    dict_list_nomat.append('IMAFLAGS_ISO_' + filter )
    print_list_nomat.append([mag_name + filter , magerr_name + '_' + filter, 'Thresh_' + filter, 'IMAFLAGS_ISO_' + filter ])


list_spec = dict_list + ['z_spec','ALPHA_J2000_spec','ALPHA_J2000_data','DELTA_J2000_spec','DELTA_J2000_data','SeqNr_spec','SeqNr_data']
list_obj = dict_list_obj + ['ALPHA_J2000','ALPHA_J2000','DELTA_J2000','DELTA_J2000','SeqNr']
list_nomat = dict_list_nomat + ['ALPHA_J2000','ALPHA_J2000','DELTA_J2000','DELTA_J2000','SeqNr']
keys_spec = reduce(lambda x,y: x + " " + y,list_spec)
keys_obj = reduce(lambda x,y: x + " " + y,list_obj)
keys_nomat = reduce(lambda x,y: x + " " + y,list_nomat)

os.system('rm /tmp/' + cluster + 'out.cat')
tempz = '/tmp/' + cluster + 'tempz'

if spec == 'yes':
    out = open('/tmp/' + cluster + 'out.cat','w')
    radec = '/tmp/' + cluster + 'radec.cat'
    outradec = open(radec,'w')
    ''' write out spectra w/ magnitudes '''
    run("ldactoasc -b -i " + matchspecfilt + " -t STDTAB -k " + keys_spec + " > " + tempz, [tempz])
    ll = open(tempz,'r').readlines()
    #out = open('/tmp/out.cat','w')
    for line in ll:
        dict = match_list(line,list_spec)
        stg = str(dict['SeqNr_data'])  + " "
        for pair in print_list: 
            if float(dict[pair[0]]) > 40:  # see if object is detected
                stg += "0\t999\t" 
            else: 
                err = dict[pair[1]]
                if float(err) < 0.03: err = 0.03
                stg += "\t%(var1).3f\t%(var2).3f\t" % {'var1':float(dict[pair[0]]),'var2':float(err)}
        z_spec = "%(var1).3f" % {'var1':float(dict['z_spec'])}
        if float(dict['z_spec']) != 0:
            stg += "\t0\t" + z_spec + "\tComment\t" #+ dict['ALPHA_J2000_spec'] + " " + dict['ALPHA_J2000_data'] 
        out.write(stg+ "\n")
        outradec.write( dict['ALPHA_J2000_spec'] + " " + dict['DELTA_J2000_spec']  + '\n')
    outradec.close()

    os.system('mkreg.pl -xcol 0 -ycol 1 -c -rad 5 -wcs -colour red ' + radec)


if arc_calc == 'yes':
    ''' write out objects w/ magnitudes '''
    run("ldactoasc -b -i " + caltablearc + " -t STDTAB -k " + keys_obj + " > " + tempz, [tempz])
    ll = open(tempz,'r').readlines()
    for line in ll:
    
        dict = match_list(line,list_obj)
    
        stg = str(dict['SeqNr'])  + "\t"
    
        for pair in print_list_obj: 
            if float(dict[pair[0]]) > 40:  # see if object is detected
                stg += " 0 999" 
            else: 
                err = float(dict[pair[1]])
                if err < 0.05: err = 0.05
                stg += "\t" + str(dict[pair[0]]) + "\t" + str(err) + "\t"
    
        #out.write(stg+ '\n')
   
if everything == 'yes':
    listcond = []
    for filter in filters:
        listcond.append('Flag_'+filter + " = 0)")
        #listcond.append('BackGr_'+filter + " > 0.00000001)")
    filt= '(' + reduce(lambda x,y: '(' + x + '  AND (' + y + ')',listcond)
    print filt
    command = 'ldacfilter -i ' + caltable + ' -t STDTAB -o /tmp/' + cluster + 'caltable -c "' + filt + ';" '
    print command
    print '\n\n\n\n'
    #os.system(command)
    #skipping FILTER!!!!
    os.system('cp ' + caltable + ' /tmp/' + cluster + 'caltable')
    
    
    
    ofile = '/tmp/' + cluster + 'out.cat' 
    out = open(ofile,'w')
    
    ''' write out objects w/ magnitudes '''
    run("ldactoasc -b -i /tmp/" + cluster + "caltable -t STDTAB -k " + keys_nomat + " > " + tempz, [tempz])
    ll = open(tempz,'r').readlines()
    for line in ll:
        dict = match_list(line,list_nomat)
    
        stg = str(dict['SeqNr'])  + "\t"

        import math
        for pair in print_list_nomat: 
            detect_mag = (2.5 * math.log10(area) + float(dict[pair[2]])) 
            flag = int(dict[pair[3]])
            if flag != 0: # if something is wrong with photometry, leave out constraint
                stg += " 0 999" 
            elif float(dict[pair[0]]) > detect_mag:  # see if object is detected, if not put detection limit
                #stg += str(detect_mag) + " -1 " 
                stg += "\t%(var1).3f\t%(var2).3f\t" % {'var1':detect_mag - 0.75,'var2':-1}
            else: 
                err = float(dict[pair[1]])
                if err < 0.05: err = 0.05
                stg += "\t" + str(dict[pair[0]]) + "\t" + str(err) + "\t" 
        #stg += "\t" + dict['ALPHA_J2000'] + " " + dict['DELTA_J2000']  + ' ' + dict['Flag_W-C-IC']
        out.write(stg+ '\n')
    out.close()
