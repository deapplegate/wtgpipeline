#!/usr/bin/env python


#def cutout(lower_mag,upper_mag,lower_diff,upper_diff,infile,outfile,color='red'):Q

def cutout(infile,color='red'):
    import os, utilities
    ppid = str(os.getppid())

    print ppid + 'a'

    #pylab.show()                 

    outfile = raw_input('name of output file?')

    color = raw_input('color of regions?')

    limits = ['lower_mag','upper_mag','lower_diff','upper_diff']
    lim_dict = {}
    for lim in limits:
        print lim + '?'
        b = raw_input()
        lim_dict[lim] = b

    utilities.run('ldacfilter -i ' + infile + ' -t PSSC\
                    -c "(((SEx_' + mag + '_' + filter + '>' + str(lim_dict['lower_mag']) + ') AND (SEx_' + mag + '_' + filter + '<' + str(lim_dict['upper_mag']) + ')) AND (magdiff>' + str(lim_dict['lower_diff']) + ')) AND (magdiff<' + str(lim_dict['upper_diff']) + ');"\
                    -o cutout1.' + ppid,['cutout1.' + ppid])
    utilities.run('ldactoasc -b -q -i cutout1.' + ppid + '  -t PSSC\
            -k Ra Dec > /tmp/' + outfile,['/tmp/' + outfile])
    utilities.run('mkreg.pl -c -rad 8 -xcol 0 -ycol 1 -wcs -colour ' + color + ' /tmp/' + outfile)

def run(command,to_delete=[]):
    for file in to_delete: os.system('rm '+ file)

    print command
    os.system(command)
    return

#filters = ['W-J-V','W-C-RC','W-C-IC','W-S-Z+']
#cluster = 'MACS2243-09'
import os
from config_bonn import appendix, cluster, tag, arc, filters, filter_root, info

#filters = ['W-S-Z+'] # ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
#cluster = 'MACS2243-09'
#filters = ['W-S-Z+']

base='/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/cat/'
#base='/tmp/'
file='all_merg.cat' 
#file='matched_SUPA0055758.cat'
mag='MAG_APER2'
magerr='MAGERR_APER2'

ThreeSecond = 0

print filters
''' need to calculate colors for 3 second exposure '''
if ThreeSecond:
    os.system('rm /tmp/workadd.cat')
    os.system('cp ' + base + file + ' /tmp/work.cat')
    print 'cp ' + base + file + ' /tmp/work.cat'
    for i in range(len(filters)):    
        info[filters[i]]['filter'] = filters[i]
        if i != len(filters) - 1:
            color1v = [filters[i],filters[i+1]]
        else:
            color1v = [filters[i-1],filters[i]]
        info[filters[i]]['color1'] = color1v[0] + 'm' + color1v[1] 
        ''' now calculate the colors '''
        magcol = ' -c "(SDSS_Mag_' + filters[i] + ' + 0);" -k FLOAT -n ' + filters[i] + 'mag "" '
        magerrcol = ' -c "(SDSS_' + magerr + '_' + filters[i] + ' + 0);" -k FLOAT -n ' + filters[i] + 'err "" '
        colorcol = ' -c "(SDSS_Mag_' + color1v[0] + ' - SDSS_Mag_' + color1v[1]+ ');" -k FLOAT -n ' + info[filters[i]]['color1'] + ' "" '
        command = 'ldaccalc -o /tmp/workadd.cat -i /tmp/work.cat -t PSSC   ' + magcol + magerrcol
        if i != len(filters) -1: 
            command += colorcol
        import os
        print command
        os.system(command)
        os.system('cp /tmp/workadd.cat /tmp/work.cat')

    os.system('cp /tmp/work.cat ' + base + '/all_merg_3sec.cat')
    file = 'all_merg_3sec.cat'

for e in info.keys():
    print e, info[e]
raw_input()

import mk_saturation_plot,os,re
os.environ['BONN_TARGET'] = cluster
os.environ['INSTRUMENT'] = 'SUBARU'

for filter in filters:
    os.environ['BONN_FILTER'] = filter 

    dict = info[filter]
    
    run('ldactoasc -b -q -i ' + base + file + '  -t PSSC\
            -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat_all',['/tmp/mk_sat_all'])

    print 'ldactoasc -b -q -i ' + base + file + '  -t PSSC\
              -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1']


    

    #'Clean!=1',
    cuts_to_make = ['Clean!=1','SEx_IMAFLAGS_ISO_' + filter + '!=0','SEx_CLASS_STAR<0.50','SEx_Flag_' + filter + '!=0']

    #cuts_to_make = ['SEx_IMAFLAGS_ISO_' + filter + '!=0','SEx_CLASS_STAR<0.50','SEx_Flag_' + filter + '!=0']

    files = ['/tmp/mk_sat_all']
    titles = ['raw']
    for cut in cuts_to_make:
        print 'making cut:', cut
        cut_name = cut.replace('>','').replace('<','')
        titles.append(cut_name)
        run('ldacfilter -i ' + base + file + ' -o /tmp/' + cut_name + ' -t PSSC\
               -c "(' + cut + ');"',['/tmp/good.stars'])

        run('ldactoasc -b -q -i /tmp/' + cut_name + '  -t PSSC\
            -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/' + cut_name + '.cat',['/tmp/' + cut_name + '.cat'])

        #mk_saturation_plot.mk_saturation('/tmp/'+cut_name + '.cat',filter)
        files.append('/tmp/' + cut_name + '.cat')

    run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
          -c "((SEx_IMAFLAGS_ISO_' + filter + '=0 AND SEx_CLASS_STAR>0.90 ) AND SEx_Flag_' + filter + '=0);"',['/tmp/good.stars'])

          #-c "(((SEx_IMAFLAGS_ISO_' + filter + '=0 AND SEx_CLASS_STAR>0.90) AND Clean=1 ) AND SEx_Flag_' + filter + '=0);"',['/tmp/good.stars'])


    #run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
    #      -c "((SEx_IMAFLAGS_ISO_' + filter + '=0 AND SEx_CLASS_STAR>0.50) AND SEx_Flag_' + filter + '=0);"',['/tmp/good.stars'])


    run('ldactoasc -b -q -i /tmp/good.stars  -t PSSC\
            -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat',['/tmp/mk_sat'])

    files.append('/tmp/mk_sat')
    titles.append('filtered')
    
    mk_saturation_plot.mk_saturation_all(files,titles,filter)

    #run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
    #            -c "(Flag=0) AND (SEx_CLASS_STAR_' + filter + '>0.90);"',['/tmp/good.stars'])

    #run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
    #      -c "((SEx_IMAFLAGS_ISO=0 AND Clean=1) AND SEx_CLASS_STAR>0.90);"',['/tmp/good.stars'])

    #run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
    #      -c "(((SEx_IMAFLAGS_ISO_' + filter + '=0 AND SEx_CLASS_STAR>0.5) AND (SEx_Flag_' + filter + '=0)) AND Clean=1);"',['/tmp/good.stars'])


    #run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
    #      -c "(Clean=1);"',['/tmp/good.stars'])


    #run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
   #             -c "(SEx_CLASS_STAR>0.00);"',['/tmp/good.stars'])

    run('ldacfilter -i /tmp/good.stars -o /tmp/good.colors -t PSSC\
                -c "(((' + dict['color1'] + '<900 AND ' + dict['color1'] + '<900) AND ' + dict['color1'] + '>-900) AND ' + dict['color1'] + '>-900);"',['/tmp/good.colors'])

    run('ldaccalc -i /tmp/good.colors -t PSSC -c "(' + dict['filter'] + 'mag - SEx_' + mag + '_' + filter + ');"  -k FLOAT -n magdiff "" -o /tmp/all.diff.cat',['/tmp/all.diff.cat'] )

    #run('ldactoasc -b -q -i /tmp/all.diff.cat -t PSSC -k SEx_' + mag + '_' + filter + ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat',['/tmp/mk_sat'] )


    run('ldactoasc -b -q -i /tmp/all.diff.cat  -t PSSC\
            -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat',['/tmp/mk_sat'])

    #cutout('/tmp/all.diff.cat','red')

    #mk_saturation_plot.mk_saturation('/tmp/mk_sat_all',filter)

    #lower_mag,upper_mag,lower_diff,upper_diff = re.split('\s+',open('box' + filter,'r').readlines()[0])

    #name = raw_input('name?')
    #cutout(lower_mag,upper_mag,lower_diff,upper_diff,'/tmp/ff.cat','lower.pos','green')
    #cutout(18,21,0.5,1,'/tmp/all.diff.cat','upper.pos','blue')
    

#    run('ldactoasc -b -q -i ' + base + file + ' -t PSSC -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat',['/tmp/mk_sat'] )

    print filter, filters
    val = raw_input("Look at the saturation plot?")
    if len(val)>0:
        if val[0] == 'y' or val[0] == 'Y':
            mk_saturation_plot.mk_saturation('/tmp/mk_sat',filter)

    val = raw_input("Make a box?")
    if len(val)>0:
        if val[0] == 'y' or val[0] == 'Y':
            mk_saturation_plot.use_box(filter)
            lower_mag,upper_mag,lower_diff,upper_diff = re.split('\s+',open('box' + filter,'r').readlines()[0])
            print lower_mag,upper_mag,lower_diff,upper_diff
            run('ldacfilter -i /tmp/all.diff.cat -t PSSC\
                        -c "(((SEx_' + mag + '_' + filter + '>' + lower_mag + ') AND (SEx_' + mag + '_' + filter + '<' + upper_mag + ')) AND (magdiff>' + lower_diff + ')) AND (magdiff<' + upper_diff + ');"\
                        -o /tmp/filt.mag.cat',['/tmp/filt.mag.cat'])

            from glob import glob
            if len(glob('/tmp/filt.mag.cat')) == 0:
                raise NoCatalogEntries

            os.system('ldactoasc -i /tmp/filt.mag.cat -t PSSC -k magdiff | wc -l')
            os.system('ldactoasc -i /tmp/all.diff.cat -t PSSC -k magdiff | wc -l')

            os.system('mv /tmp/filt.mag.cat /tmp/all.diff.cat')

            os.system('ldactoasc -i /tmp/all.diff.cat -t PSSC -k magdiff | wc -l')

    #run('ldactoasc -b -q -i /tmp/filt.mag.cat -t PSSC -k SEx_Xpos SEx_Ypos > /tmp/positions',['/tmp/positions'] )

    run('ldacaddkey -i /tmp/all.diff.cat -o /tmp/filt.airmass.cat -t PSSC -k AIRMASS 0.0 FLOAT "" ',['/tmp/filt.airmass.cat']  )
    
    run('ldactoasc -b -q -i /tmp/filt.airmass.cat -t PSSC -k SEx_' + mag + '_' + filter + ' ' + dict['filter'] + 'mag ' + dict['color1'] + ' ' + dict['color1'] + ' AIRMASS SEx_' + magerr + ' ' + dict['filter'] + 'err SEx_Xpos SEx_Ypos > /tmp/input.asc',['/tmp/input.asc'] )

    # fit photometry
    os.system("./photo_abs_new.py --input=/tmp/input.asc \
        --output=/tmp/photo_res --extinction="+str(dict['EXTCOEFF'])+" \
        --color="+str(dict['COLCOEFF'])+" --night=-1 --label="+dict['color1']+" --sigmareject=3\
         --step=STEP_1 --bandcomp="+dict['filter']+" --color1="+dict['color1']+" --color2="+dict['color1'])

    raw_input()
    

