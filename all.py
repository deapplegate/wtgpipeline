def run(command,to_delete=[]):
    for file in to_delete: os.system('rm '+ file)

    print command
    os.system(command)
    return

 
info = {'B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
    'W-J-B':{'filter':'g','color1':'gmr','color2':'umg','EXTCOEFF':-0.2104,'COLCOEFF':0.0},\
    'W-J-V':{'filter':'g','color1':'gmr','color2':'rmi','EXTCOEFF':-0.1202,'COLCOEFF':0.0},\
    'W-C-RC':{'filter':'r','color1':'rmi','color2':'gmr','EXTCOEFF':-0.0925,'COLCOEFF':0.0},\
    'W-C-IC':{'filter':'i','color1':'imz','color2':'rmi','EXTCOEFF':-0.02728,'COLCOEFF':0.0},\
    'W-S-Z+':{'filter':'z','color1':'imz','color2':'rmi','EXTCOEFF':0.0,'COLCOEFF':0.0}}

#filters = ['W-J-V','W-C-RC','W-C-IC','W-S-Z+']
#cluster = 'MACS2243-09'

from config_bonn import appendix, cluster, tag, arc, filters, filter_root

filters = ['W-J-B','W-J-V','W-C-RC','W-C-IC','W-S-Z+']
#cluster = 'MACS0911+17'

base='/nfs/slac/g/ki/ki05/anja/SUBARU/' + cluster + '/PHOTOMETRY/cat/'
file='all_merg.cat' 
mag='MAG_APER2'
magerr='MAGERR_APER2'

import mk_saturation_plot,os,re
os.environ['BONN_TARGET'] = cluster
os.environ['INSTRUMENT'] = 'SUBARU'

for filter in filters:
    os.environ['BONN_FILTER'] = filter 

    dict = info[filter]

     
    #run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
    #            -c "(Flag=0) AND (SEx_CLASS_STAR_' + filter + '>0.90);"',['/tmp/good.stars'])

    
    run('ldactoasc -b -q -i ' + base + file + '  -t PSSC\
            -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat_all',['/tmp/mk_sat_all'])



    run('ldacfilter -i ' + base + file + ' -o /tmp/good.stars -t PSSC\
                -c "((Flag=0) AND (SEx_CLASS_STAR_' + filter + '>0.90)) AND (SEx_Flag_' + filter + '=0);"',['/tmp/good.stars'])

    run('ldacfilter -i /tmp/good.stars -o /tmp/good.colors -t PSSC\
                -c "(' + dict['color1'] + '>-900) AND (' + dict['color2'] + '>-900);"',['/tmp/good.colors'])

    run('ldaccalc -i /tmp/good.colors -t PSSC -c "(' + dict['filter'] + 'mag - SEx_' + mag + '_' + filter + ');"  -k FLOAT -n magdiff "" -o /tmp/all.diff.cat',['/tmp/all.diff.cat'] )

    run('ldactoasc -b -q -i /tmp/all.diff.cat -t PSSC -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat',['/tmp/mk_sat'] )


#    run('ldactoasc -b -q -i ' + base + file + ' -t PSSC -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag SEx_FLUX_RADIUS SEx_CLASS_STAR ' + dict['filter'] + 'err ' + dict['color1'] + ' > /tmp/mk_sat',['/tmp/mk_sat'] )

    val = raw_input("Look at the saturation plot?")
    if len(val)>0:
        if val[0] == 'y' or val[0] == 'Y':
            mk_saturation_plot.mk_saturation('/tmp/mk_sat',filter)
            # make stellar saturation plot                              

    lower_mag,upper_mag,lower_diff,upper_diff = re.split('\s+',open('box' + filter,'r').readlines()[0])
    
    run('ldacfilter -i /tmp/all.diff.cat -t PSSC\
                -c "(((' + dict['filter'] + 'mag>' + lower_mag + ') AND (' + dict['filter'] + 'mag<' + upper_mag + ')) AND (magdiff>' + lower_diff + ')) AND (magdiff<' + upper_diff + ');"\
                -o /tmp/filt.mag.cat',['/tmp/filt.mag.cat'])

    run('ldactoasc -b -q -i /tmp/filt.mag.cat -t PSSC -k SEx_Xpos_' + filter +  ' SEx_Ypos_' + filter + ' > /tmp/positions',['/tmp/positions'] )

    run('ldacaddkey -i /tmp/filt.mag.cat -o /tmp/filt.airmass.cat -t PSSC -k AIRMASS 0.0 FLOAT "" ',['/tmp/filt.airmass.cat']  )
    
    run('ldactoasc -b -q -i /tmp/filt.airmass.cat -t PSSC -k SEx_' + mag + '_' + filter +  ' ' + dict['filter'] + 'mag ' + dict['color1'] + ' ' + dict['color2'] + ' AIRMASS SEx_' + magerr + '_' + filter + ' ' + dict['filter'] + 'err SEx_Xpos_' + filter + ' SEx_Ypos_' + filter + ' > /tmp/input.asc',['/tmp/input.asc'] )
        
    # fit photometry
    run("./photo_abs_new.py --input=/tmp/input.asc \
        --output=/tmp/photo_res --extinction="+str(dict['EXTCOEFF'])+" \
        --color="+str(dict['COLCOEFF'])+" --night=-1 --label="+dict['color1']+" --sigmareject=3\
         --step=STEP_1 --bandcomp="+dict['filter']+" --color1="+dict['color1']+" --color2="+dict['color2'])
    
