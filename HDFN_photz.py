import os
#os.system('python $BPZPATH/bpz.py HDFN.cat -COLUMNS HDFN.columns -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -INTERP 8 -SPECTRA CWWSB_capak.list')
import cutout_bpz

#os.system('python $BPZPATH/bpz.py HDFN.cat -OUTPUT BVR.bpz -COLUMNS BVR.columns -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -INTERP 8 -SPECTRA CWWSB_capak.list')
#cutout_bpz.plot_res('BVR.bpz','BVR')
#os.system('python $BPZPATH/bpz.py HDFN.cat -OUTPUT VRI.bpz -COLUMNS VRI.columns -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -INTERP 8 -SPECTRA CWWSB_capak.list')
#cutout_bpz.plot_res('VRI.bpz','VRI')
#raw_input()

#os.system('python $BPZPATH/bpz.py HDFN.cat -OUTPUT BVRI.bpz -COLUMNS BVRI.columns -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -INTERP 8 -SPECTRA CWWSB_capak.list')
#cutout_bpz.plot_res('BVRI.bpz','BVRI')
#os.system('python $BPZPATH/bpz.py HDFN.cat -OUTPUT BVIz.bpz -COLUMNS BVIz.columns -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -INTERP 8 -SPECTRA CWWSB_capak.list')
#cutout_bpz.plot_res('BVIz.bpz','BVIz')
#os.system('python $BPZPATH/bpz.py HDFN.cat -OUTPUT VRIz.bpz -COLUMNS VRIz.columns -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -INTERP 8 -SPECTRA CWWSB_capak.list')
#cutout_bpz.plot_res('VRIz.bpz','VRIz')


#os.system('python $BPZPATH/bpz.py HDFN.cat -OUTPUT BVRIz.bpz -COLUMNS BVRIz.columns -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -INTERP 8 -SPECTRA CWWSB_capak.list')
#cutout_bpz.plot_res('BVRIz.bpz','BVRIz')


os.system('python $BPZPATH/bpz.py HDFN.cat -OUTPUT BVRI.bpz -COLUMNS BVRI.columns -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -INTERP 8 -SPECTRA CWWSB_capak.list')
cutout_bpz.plot_res('BVRI.bpz','BVRI')
