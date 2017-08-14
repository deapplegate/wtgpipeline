import re,os
os.putenv('INSTRUMENT','SUBARU')
os.system("rm /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/2007-07-18_skyflat_test/SKYFLAT//BINNED/div_1993_1994_CLIPMEAN_2.0_2.0_chip_mos.fits")
os.system("rm /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/2007-07-18_skyflat_test/SKYFLAT//BINNED/div_1993_1994_CLIPMEAN_2.0_2.0_chip_mos_normal.fits")
os.system("./create_binnedmosaics.sh /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/2007-07-18_skyflat_test/ SKYFLAT div_1993_1994_CLIPMEAN_2.0_2.0_chip '' 8 -32 ")
os.system("imstats /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/2007-07-18_skyflat_test/SKYFLAT/div_1993_1994_CLIPMEAN_2.0_2.0_chip_1.fits -s 500 1500 1500 2500 -o outlist")
p = open('outlist').readlines()[-1]
mode = re.split('\s+',p)[1]
os.system("ic '%1 " + mode + " / ' /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/2007-07-18_skyflat_test/SKYFLAT//BINNED/div_1993_1994_CLIPMEAN_2.0_2.0_chip_mos.fits > /nfs/slac/g/ki/ki02/xoc/anja/SUBARU/2007-07-18_skyflat_test/SKYFLAT//BINNED/div_1993_1994_CLIPMEAN_2.0_2.0_chip_mos_normal.fits")
