import os, cutout_bpz
os.system('python $BPZPATH/bpz.py HDFN.cat -OUTPUT UBVRIz.bpz -COLUMNS UBVRIz.columns -PROBS_LITE UBVRIz.probs -MAG yes -PRIOR hdfn_SB -ZMAX 4.0 -MIN_RMS 0.05 -INTERP 8 -SPECTRA CWWSB_capak.list')
cutout_bpz.plot_res('UBVRIz.bpz','UBVRIz')
