#! /usr/bin/env python
import numpy
import sys
sys.path.append("/u/ki/awright/wtgpipeline/")
import ldac
import astropy.io.fits as pyfits
import astropy
import pickle
import glob
from matplotlib.pylab import *

pdz2015fo=pyfits.open("/u/ki/awright/COSMOS_2017/COSMOS_2015/pdz_cosmos2015_v1.3.fits")
pdz2015=ldac.LDACCat(pdz2015fo[1])

hdulist = pyfits.open('/u/ki/awright/COSMOS_2017/COSMOS_2015/COSMOS2015_Laigle+_v1.1.fits')
cat2015 = ldac.LDACCat(hdulist[1])                                                                                                                                             

#tmp#pdznewfo=pyfits.open("/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/pdz_v2.0_010312.fits")
#tmp#pdznew=ldac.LDACCat(pdznewfo[1])

hdulist_4cc = pyfits.open('/u/ki/dapple/nfs12/cosmos/cosmos_4cc.cat')
cat4cc = ldac.LDACCat(hdulist_4cc[1])                                                                                                                                             
print "cat4cc.keys()==['SeqNr', 'NFILT', 'MAG_APER1-SUBARU-COADD-1-W-S-I+', 'MAG_APER1-MEGAPRIME-COADD-1-z', 'MAG_APER1-SUBARU-COADD-1-W-J-B', 'MAG_APER1-SUBARU-COADD-1-W-S-Z+', 'MAG_APER1-SUBARU-COADD-1-W-S-G+', 'MAG_APER1-SUBARU-COADD-1-W-C-RC', 'MAG_APER1-MEGAPRIME-COADD-1-r', 'MAG_APER1-MEGAPRIME-COADD-1-i', 'MAG_APER1-SUBARU-COADD-1-W-S-R+', 'MAG_APER1-SUBARU-COADD-1-W-C-IC', 'MAG_APER1-SUBARU-COADD-1-W-J-V', 'MAG_APER1-MEGAPRIME-COADD-1-g', 'DATA_SeqNr', 'DATA_MAG_APER-SUBARU-COADD-1-W-S-I+', 'DATA_MAGERR_APER-SUBARU-10_2-1-W-S-I+', 'DATA_MAG_APER-MEGAPRIME-COADD-1-z', 'DATA_MAGERR_APER-MEGAPRIME-0-1-z', 'DATA_MAG_APER-SUBARU-COADD-1-W-J-B', 'DATA_MAGERR_APER-SUBARU-10_2-1-W-J-B', 'DATA_MAG_APER-SUBARU-COADD-1-W-S-Z+', 'DATA_MAGERR_APER-SUBARU-10_2-1-W-S-Z+', 'DATA_MAG_APER-SUBARU-COADD-1-W-S-G+', 'DATA_MAGERR_APER-SUBARU-10_2-1-W-S-G+', 'DATA_MAG_APER-SUBARU-COADD-1-W-C-RC', 'DATA_MAGERR_APER-SUBARU-10_2-1-W-C-RC', 'DATA_MAG_APER-MEGAPRIME-COADD-1-r', 'DATA_MAGERR_APER-MEGAPRIME-0-1-r', 'DATA_MAG_APER-MEGAPRIME-COADD-1-i', 'DATA_MAGERR_APER-MEGAPRIME-0-1-i', 'DATA_MAG_APER-SUBARU-COADD-1-W-S-R+', 'DATA_MAGERR_APER-SUBARU-10_2-1-W-S-R+', 'DATA_MAG_APER-SUBARU-COADD-1-W-C-IC', 'DATA_MAGERR_APER-SUBARU-10_2-1-W-C-IC', 'DATA_MAG_APER-SUBARU-COADD-1-W-J-V', 'DATA_MAGERR_APER-SUBARU-10_2-1-W-J-V', 'DATA_MAG_APER-MEGAPRIME-COADD-1-g', 'DATA_MAGERR_APER-MEGAPRIME-0-1-g', 'DATA_PatID', 'DATA_zspec', 'DATA_priormag', 'DATA_NFILT', 'Ra', 'Dec', 'rg', 'zp_best', 'A_IMAGE', 'B_IMAGE', 'FWHM_IMAGE', 'CLASS_STAR', 'auto_flag', 'det_iso', 'ddet_iso', 'det_auto', 'ddet_auto', 'J', 'K', 'type', 'acs_fwhm', 'acs_star', 'zphot', 'V_mask', 'i_mask', 'z_mask', 'deep_mask', 'HYBRID_MAG_APER-SUBARU-10_2-1-W-S-I+']"
catold = ldac.openObjectFile('/u/ki/dapple/nfs12/cosmos/cosmos.cat')
match_2015,match_4cc,unmatch_2015,unmatch_4cc = ldac.orderedmatchById(cat2015, cat4cc, 'ID2008', 'SeqNr')
f1=figure(figsize=(14,7))
suptitle("catalog on x axis=2015 cat &&&  catalog on y axis = old cosmos_4cc.cat")
f1.add_subplot(121)
plot(match_2015['ALPHA_J2000'],match_4cc['Ra'],'ko')
xlabel('ALPHA_J2000');ylabel('Ra')
grid()
f1.add_subplot(122)
plot(match_2015['DELTA_J2000'],match_4cc['Dec'],'ko')
xlabel('DELTA_J2000');ylabel('Dec')
grid()
f1.savefig('plt_cosmos_ra_dec_compare')
sys.exit()
## difference in keys, but not objects between these two:
#tmp# catnewzp=ldac.openObjectFile("/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.zp.cat")
#tmp# catnew=ldac.openObjectFile("/u/ki/dapple/nfs12/cosmos/ultravista_cosmos/newphotcat/cosmos.matched.cat")
#yes: len(newcat)==len(newzpcat)
#no: newcat == newzpcat
print ' catold.keys()=',catold.keys()
#tmp# print ' catnew.keys()=',catnew.keys()
#tmp# print ' catnewzp.keys()=',catnewzp.keys()
#tmp# print ' pdznew.keys()=',pdznew.keys()
print ' cat2015.keys()=',cat2015.keys()
print ' pdz2015.keys()=',pdz2015.keys()
# catold.keys()= ['id', 'tile', 'ra', 'dec', 'clon', 'clat', 'zp_best', 'type', 'zp_gal', 'zl68_gal', 'zu68_gal', 'zl99_gal', 'zu99_gal', 'chi_gal', 'ebv', 'zp_sec', 'chi_sec', 'ebv_sec', 'mod_star', 'chi_star', 'umag', 'bmag', 'vmag', 'gmag', 'rmag', 'imag', 'zmag', 'icmag', 'jmag', 'kmag', 'eu', 'eb', 'ev', 'eg', 'er', 'ei', 'ez', 'eic', 'ej', 'ek', 'flagb', 'flagv', 'flagi', 'flagz', 'flagd', 'nbfilt', 'i_auto', 'auto_offset', 'auto_flag', 'mv']

# catnew.keys()= ['gp', 'dIB484', 'F814W', 'i_max', 'dIB527', 'dH1', 'K_uv', 'NB816', 'z_s', 'IB738', 'ID_2006', 'i_auto', 'dH_uv', 'i_star', 'H', 'du_s', 'F814W_star', 'J_uv', 'dch3', 'dIB738', 'du', 'dIB827', 'IB427', 'dJ', 'dH', 'dB', 'H_uv', 'IB505', 'J3', 'dch2', 'dV', 'x', 'dip', 'IB624', 'FUV', 'dIB505', 'dJ3', 'dJ2', 'dKs', 'di_s', 'Eb-v', 'J2', 'g_s', 'J1', 'dIB624', 'dK_uv', 'dKc', 'di_c', 'zp', 'rp', 'dKnf', 'dH2', 'appflag', 'ra', 'photflag', 'dF814W', 'dNUV', 'auto_offset', 'ID_2008', 'acs_mask', 'dNB816', 'di_auto', 'H2', 'drp', 'H1', 'dIB427', 'dzp', 'dFUV', 'deep_mask', 'V_mask', 'dJ1', 'dIB767', 'z_mask', 'dg_s', 'i_mask', 'IB574', 'dzpp', 'NUV', 'zpp', 'blendflag', 'mask_NUV', 'IB679', 'Kc', 'B', 'J', 'F814W_fwhm', 'Ks', 'dIB574', 'det_fwhm', 'dIB679', 'V', 'i_fwhm', 'IB709', 'ch1', 'ch2', 'ch3', 'ch4', 'IB767', 'mask_FUV', 'dec', 'IRAC2_mask', 'ip', 'i_c', 'i_s', 'dIB709', 'dz_s', 'dJ_uv', 'r_s', 'dY_uv', 'u_s', 'Kc_mask', 'B_mask', 'auto_flag', 'tile', 'flags', 'dch1', 'IRAC1_mask', 'dch4', 'acsdata_mask', 'dNB711', 'Knf', 'y', 'dgp', 'IB827', 'ID', 'NB711', 'IB464', 'Y_uv', 'IB527', 'u', 'objID', 'dr_s', 'IB484', 'dIB464']

# catnewzp.keys()= ['zchi', 'M_j', 'M_i', 'M_k', 'BCmass', 'BCsfr', 'zerr_chi_min', 'chipdf', 'M_g', 'M_FUV', 'M_z', 'chisq', 'L_k', 'BCsfr_min', 'M_r', 'M_u', 'zqso', 'BCmodel', 'zerr_chi_max', 'ACSstar', 'M_B', 'star_model', 'BCssfr_min', 'galaxy_model', 'ra', 'qso_model', 'DCnuv-r', 'type', 'chistar', 'BCssfr_max', 'L_nu', 'zqsochi', 'L_r', 'BCext', 'zpdf', 'zphot', 'ID', 'zerr_pdf_min', 'BCmass_min', 'dec', 'BCsfr_max', 'M_NUV', 'BCage', 'zphot2', 'BCmass_max', 'BCssfr', 'zerr_pdf_max', 'M_V', 'Ebv', 'Nbands', 'objID', 'chisq2', 'Mass_2006', 'Ext_law']
# cat2015.keys()= ['ALPHA_J2000', 'DELTA_J2000', 'NUMBER', 'X_IMAGE', 'Y_IMAGE', 'ERRX2_IMAGE', 'ERRY2_IMAGE', 'ERRXY_IMAGE', 'FLAG_HJMCC', 'FLUX_RADIUS', 'KRON_RADIUS', 'EBV', 'FLAG_PETER', 'FLAG_COSMOS', 'FLAG_DEEP', 'FLAG_SHALLOW', 'Ks_FLUX_APER2', 'Ks_FLUXERR_APER2', 'Ks_FLUX_APER3', 'Ks_FLUXERR_APER3', 'Ks_MAG_APER2', 'Ks_MAGERR_APER2', 'Ks_MAG_APER3', 'Ks_MAGERR_APER3', 'Ks_MAG_AUTO', 'Ks_MAGERR_AUTO', 'Ks_MAG_ISO', 'Ks_MAGERR_ISO', 'Ks_FLAGS', 'Ks_IMAFLAGS_ISO', 'Y_FLUX_APER2', 'Y_FLUXERR_APER2', 'Y_FLUX_APER3', 'Y_FLUXERR_APER3', 'Y_MAG_APER2', 'Y_MAGERR_APER2', 'Y_MAG_APER3', 'Y_MAGERR_APER3', 'Y_MAG_AUTO', 'Y_MAGERR_AUTO', 'Y_MAG_ISO', 'Y_MAGERR_ISO', 'Y_FLAGS', 'Y_IMAFLAGS_ISO', 'H_FLUX_APER2', 'H_FLUXERR_APER2', 'H_FLUX_APER3', 'H_FLUXERR_APER3', 'H_MAG_APER2', 'H_MAGERR_APER2', 'H_MAG_APER3', 'H_MAGERR_APER3', 'H_MAG_AUTO', 'H_MAGERR_AUTO', 'H_MAG_ISO', 'H_MAGERR_ISO', 'H_FLAGS', 'H_IMAFLAGS_ISO', 'J_FLUX_APER2', 'J_FLUXERR_APER2', 'J_FLUX_APER3', 'J_FLUXERR_APER3', 'J_MAG_APER2', 'J_MAGERR_APER2', 'J_MAG_APER3', 'J_MAGERR_APER3', 'J_MAG_AUTO', 'J_MAGERR_AUTO', 'J_MAG_ISO', 'J_MAGERR_ISO', 'J_FLAGS', 'J_IMAFLAGS_ISO', 'B_FLUX_APER2', 'B_FLUXERR_APER2', 'B_FLUX_APER3', 'B_FLUXERR_APER3', 'B_MAG_APER2', 'B_MAGERR_APER2', 'B_MAG_APER3', 'B_MAGERR_APER3', 'B_MAG_AUTO', 'B_MAGERR_AUTO', 'B_MAG_ISO', 'B_MAGERR_ISO', 'B_FLAGS', 'B_IMAFLAGS_ISO', 'V_FLUX_APER2', 'V_FLUXERR_APER2', 'V_FLUX_APER3', 'V_FLUXERR_APER3', 'V_MAG_APER2', 'V_MAGERR_APER2', 'V_MAG_APER3', 'V_MAGERR_APER3', 'V_MAG_AUTO', 'V_MAGERR_AUTO', 'V_MAG_ISO', 'V_MAGERR_ISO', 'V_FLAGS', 'V_IMAFLAGS_ISO', 'ip_FLUX_APER2', 'ip_FLUXERR_APER2', 'ip_FLUX_APER3', 'ip_FLUXERR_APER3', 'ip_MAG_APER2', 'ip_MAGERR_APER2', 'ip_MAG_APER3', 'ip_MAGERR_APER3', 'ip_MAG_AUTO', 'ip_MAGERR_AUTO', 'ip_MAG_ISO', 'ip_MAGERR_ISO', 'ip_FLAGS', 'ip_IMAFLAGS_ISO', 'r_FLUX_APER2', 'r_FLUXERR_APER2', 'r_FLUX_APER3', 'r_FLUXERR_APER3', 'r_MAG_APER2', 'r_MAGERR_APER2', 'r_MAG_APER3', 'r_MAGERR_APER3', 'r_MAG_AUTO', 'r_MAGERR_AUTO', 'r_MAG_ISO', 'r_MAGERR_ISO', 'r_FLAGS', 'r_IMAFLAGS_ISO', 'u_FLUX_APER2', 'u_FLUXERR_APER2', 'u_FLUX_APER3', 'u_FLUXERR_APER3', 'u_MAG_APER2', 'u_MAGERR_APER2', 'u_MAG_APER3', 'u_MAGERR_APER3', 'u_MAG_AUTO', 'u_MAGERR_AUTO', 'u_MAG_ISO', 'u_MAGERR_ISO', 'u_FLAGS', 'u_IMAFLAGS_ISO', 'zp_FLUX_APER2', 'zp_FLUXERR_APER2', 'zp_FLUX_APER3', 'zp_FLUXERR_APER3', 'zp_MAG_APER2', 'zp_MAGERR_APER2', 'zp_MAG_APER3', 'zp_MAGERR_APER3', 'zp_MAG_AUTO', 'zp_MAGERR_AUTO', 'zp_MAG_ISO', 'zp_MAGERR_ISO', 'zp_FLAGS', 'zp_IMAFLAGS_ISO', 'zpp_FLUX_APER2', 'zpp_FLUXERR_APER2', 'zpp_FLUX_APER3', 'zpp_FLUXERR_APER3', 'zpp_MAG_APER2', 'zpp_MAGERR_APER2', 'zpp_MAG_APER3', 'zpp_MAGERR_APER3', 'zpp_MAG_AUTO', 'zpp_MAGERR_AUTO', 'zpp_MAG_ISO', 'zpp_MAGERR_ISO', 'zpp_FLAGS', 'zpp_IMAFLAGS_ISO', 'IA484_FLUX_APER2', 'IA484_FLUXERR_APER2', 'IA484_FLUX_APER3', 'IA484_FLUXERR_APER3', 'IA484_MAG_APER2', 'IA484_MAGERR_APER2', 'IA484_MAG_APER3', 'IA484_MAGERR_APER3', 'IA484_MAG_AUTO', 'IA484_MAGERR_AUTO', 'IA484_MAG_ISO', 'IA484_MAGERR_ISO', 'IA484_FLAGS', 'IA484_IMAFLAGS_ISO', 'IA527_FLUX_APER2', 'IA527_FLUXERR_APER2', 'IA527_FLUX_APER3', 'IA527_FLUXERR_APER3', 'IA527_MAG_APER2', 'IA527_MAGERR_APER2', 'IA527_MAG_APER3', 'IA527_MAGERR_APER3', 'IA527_MAG_AUTO', 'IA527_MAGERR_AUTO', 'IA527_MAG_ISO', 'IA527_MAGERR_ISO', 'IA527_FLAGS', 'IA527_IMAFLAGS_ISO', 'IA624_FLUX_APER2', 'IA624_FLUXERR_APER2', 'IA624_FLUX_APER3', 'IA624_FLUXERR_APER3', 'IA624_MAG_APER2', 'IA624_MAGERR_APER2', 'IA624_MAG_APER3', 'IA624_MAGERR_APER3', 'IA624_MAG_AUTO', 'IA624_MAGERR_AUTO', 'IA624_MAG_ISO', 'IA624_MAGERR_ISO', 'IA624_FLAGS', 'IA624_IMAFLAGS_ISO', 'IA679_FLUX_APER2', 'IA679_FLUXERR_APER2', 'IA679_FLUX_APER3', 'IA679_FLUXERR_APER3', 'IA679_MAG_APER2', 'IA679_MAGERR_APER2', 'IA679_MAG_APER3', 'IA679_MAGERR_APER3', 'IA679_MAG_AUTO', 'IA679_MAGERR_AUTO', 'IA679_MAG_ISO', 'IA679_MAGERR_ISO', 'IA679_FLAGS', 'IA679_IMAFLAGS_ISO', 'IA738_FLUX_APER2', 'IA738_FLUXERR_APER2', 'IA738_FLUX_APER3', 'IA738_FLUXERR_APER3', 'IA738_MAG_APER2', 'IA738_MAGERR_APER2', 'IA738_MAG_APER3', 'IA738_MAGERR_APER3', 'IA738_MAG_AUTO', 'IA738_MAGERR_AUTO', 'IA738_MAG_ISO', 'IA738_MAGERR_ISO', 'IA738_FLAGS', 'IA738_IMAFLAGS_ISO', 'IA767_FLUX_APER2', 'IA767_FLUXERR_APER2', 'IA767_FLUX_APER3', 'IA767_FLUXERR_APER3', 'IA767_MAG_APER2', 'IA767_MAGERR_APER2', 'IA767_MAG_APER3', 'IA767_MAGERR_APER3', 'IA767_MAG_AUTO', 'IA767_MAGERR_AUTO', 'IA767_MAG_ISO', 'IA767_MAGERR_ISO', 'IA767_FLAGS', 'IA767_IMAFLAGS_ISO', 'IB427_FLUX_APER2', 'IB427_FLUXERR_APER2', 'IB427_FLUX_APER3', 'IB427_FLUXERR_APER3', 'IB427_MAG_APER2', 'IB427_MAGERR_APER2', 'IB427_MAG_APER3', 'IB427_MAGERR_APER3', 'IB427_MAG_AUTO', 'IB427_MAGERR_AUTO', 'IB427_MAG_ISO', 'IB427_MAGERR_ISO', 'IB427_FLAGS', 'IB427_IMAFLAGS_ISO', 'IB464_FLUX_APER2', 'IB464_FLUXERR_APER2', 'IB464_FLUX_APER3', 'IB464_FLUXERR_APER3', 'IB464_MAG_APER2', 'IB464_MAGERR_APER2', 'IB464_MAG_APER3', 'IB464_MAGERR_APER3', 'IB464_MAG_AUTO', 'IB464_MAGERR_AUTO', 'IB464_MAG_ISO', 'IB464_MAGERR_ISO', 'IB464_FLAGS', 'IB464_IMAFLAGS_ISO', 'IB505_FLUX_APER2', 'IB505_FLUXERR_APER2', 'IB505_FLUX_APER3', 'IB505_FLUXERR_APER3', 'IB505_MAG_APER2', 'IB505_MAGERR_APER2', 'IB505_MAG_APER3', 'IB505_MAGERR_APER3', 'IB505_MAG_AUTO', 'IB505_MAGERR_AUTO', 'IB505_MAG_ISO', 'IB505_MAGERR_ISO', 'IB505_FLAGS', 'IB505_IMAFLAGS_ISO', 'IB574_FLUX_APER2', 'IB574_FLUXERR_APER2', 'IB574_FLUX_APER3', 'IB574_FLUXERR_APER3', 'IB574_MAG_APER2', 'IB574_MAGERR_APER2', 'IB574_MAG_APER3', 'IB574_MAGERR_APER3', 'IB574_MAG_AUTO', 'IB574_MAGERR_AUTO', 'IB574_MAG_ISO', 'IB574_MAGERR_ISO', 'IB574_FLAGS', 'IB574_IMAFLAGS_ISO', 'IB709_FLUX_APER2', 'IB709_FLUXERR_APER2', 'IB709_FLUX_APER3', 'IB709_FLUXERR_APER3', 'IB709_MAG_APER2', 'IB709_MAGERR_APER2', 'IB709_MAG_APER3', 'IB709_MAGERR_APER3', 'IB709_MAG_AUTO', 'IB709_MAGERR_AUTO', 'IB709_MAG_ISO', 'IB709_MAGERR_ISO', 'IB709_FLAGS', 'IB709_IMAFLAGS_ISO', 'IB827_FLUX_APER2', 'IB827_FLUXERR_APER2', 'IB827_FLUX_APER3', 'IB827_FLUXERR_APER3', 'IB827_MAG_APER2', 'IB827_MAGERR_APER2', 'IB827_MAG_APER3', 'IB827_MAGERR_APER3', 'IB827_MAG_AUTO', 'IB827_MAGERR_AUTO', 'IB827_MAG_ISO', 'IB827_MAGERR_ISO', 'IB827_FLAGS', 'IB827_IMAFLAGS_ISO', 'NB711_FLUX_APER2', 'NB711_FLUXERR_APER2', 'NB711_FLUX_APER3', 'NB711_FLUXERR_APER3', 'NB711_MAG_APER2', 'NB711_MAGERR_APER2', 'NB711_MAG_APER3', 'NB711_MAGERR_APER3', 'NB711_MAG_AUTO', 'NB711_MAGERR_AUTO', 'NB711_MAG_ISO', 'NB711_MAGERR_ISO', 'NB711_FLAGS', 'NB711_IMAFLAGS_ISO', 'NB816_FLUX_APER2', 'NB816_FLUXERR_APER2', 'NB816_FLUX_APER3', 'NB816_FLUXERR_APER3', 'NB816_MAG_APER2', 'NB816_MAGERR_APER2', 'NB816_MAG_APER3', 'NB816_MAGERR_APER3', 'NB816_MAG_AUTO', 'NB816_MAGERR_AUTO', 'NB816_MAG_ISO', 'NB816_MAGERR_ISO', 'NB816_FLAGS', 'NB816_IMAFLAGS_ISO', 'SPLASH_1_FLUX', 'SPLASH_1_FLUX_ERR', 'SPLASH_1_MAG', 'SPLASH_1_MAGERR', 'SPLASH_2_FLUX', 'SPLASH_2_FLUX_ERR', 'SPLASH_2_MAG', 'SPLASH_2_MAGERR', 'SPLASH_3_FLUX', 'SPLASH_3_FLUX_ERR', 'SPLASH_3_MAG', 'SPLASH_3_MAGERR', 'SPLASH_4_FLUX', 'SPLASH_4_FLUX_ERR', 'SPLASH_4_MAG', 'SPLASH_4_MAGERR', 'Hw_FLUX_APER2', 'Hw_FLUXERR_APER2', 'Hw_FLUX_APER3', 'Hw_FLUXERR_APER3', 'Hw_MAG_APER2', 'Hw_MAGERR_APER2', 'Hw_MAG_APER3', 'Hw_MAGERR_APER3', 'Hw_MAG_AUTO', 'Hw_MAGERR_AUTO', 'Hw_MAG_ISO', 'Hw_MAGERR_ISO', 'Hw_FLAGS', 'Hw_IMAFLAGS_ISO', 'Ksw_FLUX_APER2', 'Ksw_FLUXERR_APER2', 'Ksw_FLUX_APER3', 'Ksw_FLUXERR_APER3', 'Ksw_MAG_APER2', 'Ksw_MAGERR_APER2', 'Ksw_MAG_APER3', 'Ksw_MAGERR_APER3', 'Ksw_MAG_AUTO', 'Ksw_MAGERR_AUTO', 'Ksw_MAG_ISO', 'Ksw_MAGERR_ISO', 'Ksw_FLAGS', 'Ksw_IMAFLAGS_ISO', 'yHSC_FLUX_APER2', 'yHSC_FLUXERR_APER2', 'yHSC_FLUX_APER3', 'yHSC_FLUXERR_APER3', 'yHSC_MAG_APER2', 'yHSC_MAGERR_APER2', 'yHSC_MAG_APER3', 'yHSC_MAGERR_APER3', 'yHSC_MAG_AUTO', 'yHSC_MAGERR_AUTO', 'yHSC_MAG_ISO', 'yHSC_MAGERR_ISO', 'yHSC_FLAGS', 'yHSC_IMAFLAGS_ISO', 'FLUX_24', 'FLUXERR_24', 'MAG_24', 'MAGERR_24', 'ID_A24', 'FLUX_100', 'FLUXERR_100', 'FLUX_160', 'FLUXERR_160', 'FLUX_250', 'FLUXERR_250', 'FLUXERRTOT_250', 'FLUX_350', 'FLUXERR_350', 'FLUXERRTOT_350', 'FLUX_500', 'FLUXERR_500', 'FLUXERRTOT_500', 'ID_CHANDRA2016', 'ID2006', 'ID2008', 'ID2013', 'MAG_GALEX_NUV', 'MAGERR_GALEX_NUV', 'MAG_GALEX_FUV', 'MAGERR_GALEX_FUV', 'FLUX_GALEX_NUV', 'FLUXERR_GALEX_NUV', 'FLUX_GALEX_FUV', 'FLUXERR_GALEX_FUV', 'FLUX_814W', 'FLUXERR_814W', 'NAME_VLA90CM', 'FLUXPEAK_90CM', 'FLUXPEAKERR_90CM', 'FLUXINT_90CM', 'FLUXINTERR_90CM', 'RMSBKG_90CM', 'NAME_JVLDEEP', 'NAME_JVLLARGE', 'FLUXPEAK_20CM', 'FLUXPEAKERR_20CM', 'FLUXINT_20CM', 'FLUXINTERR_20CM', 'RMSBKG_20CM', 'ID_XMM', 'FLUX_XMM_0.5_2', 'FLUX_XMM_2_10', 'FLUX_XMM_5_10', 'HARDNESS_XMM', 'ID_CHANDRA09', 'FLUX_CHANDRA_0.5_2', 'FLUX_CHANDRA_2_10', 'FLUX_CHANDRA_0.5_10', 'ID_NUSTAR', 'FLUX_NUSTAR_3_24', 'FLUXERR_NUSTAR_3_24', 'FLUX_NUSTAR_3_8', 'FLUXERR_NUSTAR_3_8', 'FLUX_NUSTAR_8_24', 'FLUXERR_NUSTAR_8_24', 'HARDNESS_NUSTAR', 'HARDNESSLOW_NUSTAR', 'HARDNESSUP_NUSTAR', 'FLAG_XRAYBLEND', 'OFFSET', 'PHOTOZ', 'TYPE', 'ZPDF', 'ZPDF_L68', 'ZPDF_H68', 'ZMINCHI2', 'CHI2_BEST', 'ZP_2', 'CHI2_2', 'NBFILT', 'ZQ', 'CHIQ', 'MODQ', 'MODS', 'CHIS', 'MODEL', 'AGE', 'EXTINCTION', 'MNUV', 'MU', 'MB', 'MV', 'MR', 'MI', 'MZ', 'MY', 'MJ', 'MH', 'MK', 'MNUV_MR', 'CLASS', 'MASS_MED', 'MASS_MED_MIN68', 'MASS_MED_MAX68', 'MASS_BEST', 'SFR_MED', 'SFR_MED_MIN68', 'SFR_MED_MAX68', 'SFR_BEST', 'SSFR_MED', 'SSFR_MED_MIN68', 'SSFR_MED_MAX68', 'SSFR_BEST', 'L_NU', 'L_R', 'L_K']

# pdz2015.keys()= ['ID', 'RA', 'DEC', 'FL', 'FLK', 'Z_FINAL', 'TY', 'Z_MED_PDZ', 'Z_MIN68', 'Z_MAX68', 'ZMIN_CHI2', 'SECOND_PEAK', 'ZS', 'FLZ', 'NUV', 'DNUV', 'U', 'DU', 'B', 'DB', 'V', 'DV', 'R', 'DR', 'I', 'DI', 'ZN', 'DZN', 'YHSC', 'DYHSC', 'Y', 'DY', 'J', 'DJ', 'H', 'DH', 'K', 'DK', 'IA427', 'DIA427', 'IA464', 'DIA464', 'IA484', 'DIA484', 'IA505', 'DIA505', 'IA527', 'DIA527', 'IA574', 'DIA574', 'IA624', 'DIA624', 'IA679', 'DIA679', 'IA709', 'DIA709', 'IA738', 'DIA738', 'IA767', 'DIA767', 'IA827', 'DIA827', 'NB711', 'DNB711', 'NB816', 'DNB816', 'CH1', 'DCH1', 'CH2', 'DCH2', 'CH3', 'DCH3', 'CH4', 'DCH4']

# pdznew.keys()= ['ID', 'RA', 'DEC', 'Z_FINAL', 'TY', 'Z_MED_PDZ', 'Z_MIN68', 'Z_MAX68', 'ZMIN_CHI2', 'SECOND_PEAK']


def matchById(thiscat, othercat, otherid='SeqNr', thisid='SeqNr'):
        '''Returns a subset of this catalog, that matches the order of the provided catalog'''

        order = {}
        unmatchedorder = {}
        for i, x in enumerate(thiscat[thisid]):
            order[x] = i

        for i, x in enumerate(othercat[otherid]):
            unmatchedorder[x] = i

        keepOrder = []
        missingOrder = []
        for x in othercat[otherid]:
            if x in order:
                keepOrder.append(order[x])
            else:                                                                                                                                                          
                missingOrder.append(unmatchedorder[x])                          

        keep = numpy.array(keepOrder)
        missing = numpy.array(missingOrder)
        matched = thiscat.filter(keep)
        unmatched = othercat.filter(missing)
        return matched,unmatched


#match_new, unmatch_new = matchById(catnew, catold, 'id', 'ID_2008')
match_2015, unmatch_2015 = matchById(cat2015, catold, 'id', 'ID2008')
match_old, unmatch_old = matchById(catold, cat2015, 'ID2008', 'id')

print ' len(match_2015)=',len(match_2015) , ' len(unmatch_2015)=',len(unmatch_2015) , ' len(match_old)=',len(match_old) , ' len(unmatch_old)=',len(unmatch_old)

id_sort=argsort(match_2015['ID2008'])
ordered2015=match_2015.filter(id_sort)
id_sort=argsort(match_old['id'])
orderedold=match_old.filter(id_sort)
(ordered2015['ID2008']==orderedold['id']).all()
f1=figure()
plot(ordered2015['ALPHA_J2000'],orderedold['ra'],'ko')
f2=figure()
plot(ordered2015['DELTA_J2000'],orderedold['dec'],'ko')


raoff=(ordered2015['ALPHA_J2000']-orderedold['ra'])
decoff=(ordered2015['DELTA_J2000']-orderedold['dec'])
posoff=sqrt(raoff**2 + decoff**2)
posoff.max()
print posoff.max()

sys.exit()
for id in catold['id']:
	if (catnew['ID_2008']==id).sum()>2:
		print id
		break

#id2008_col=hdu.columns['ID2008']
#new_cols = pyfits.ColDefs([id2008_col])
#newhdu = pyfits.BinTableHDU.from_columns(pdz2015cols+new_cols)
#newhdu.writeto("/u/ki/awright/COSMOS_2017/COSMOS_2015/pdz_cosmos2015_ID2008_added.fits")
#id2008=id2008_col.array
#(id2008>0).sum()
#newdata=newhdu.data
#newer=newdata[(id2008>0)]
#hdu2 = pyfits.BinTableHDU(data=newer)
#hdu2.writeto("/u/ki/awright/COSMOS_2017/COSMOS_2015/pdz_cosmos2015_ID2008_shorter.fits")

pdz15_match_old=pdz15.matchById(oldcat,"id","ID2008")
pdzv2_match_old=pdzv2.matchById(oldcat,"id","ID")
print len(pdzv2_match_old)
print len(pdz15_match_old)
print len(pdzv2)
print len(pdz15)


def cat_id_row(cat,equal_val,key="ID",dict_keys=None):
	col = cat[key]
	equal_index=col.searchsorted(equal_val)
	print equal_index,col[equal_index],equal_val
	if col[equal_index]==equal_val:
		equal_row=cat[equal_index]
		if dict_keys==None:
			try:
				dict_keys=cat.keys()
			except AttributeError:
				dict_keys=cat.names
		dict_row={}
		for k,v in zip(dict_keys,equal_row):
			dict_row[k]=v
		return equal_index,equal_row,dict_row

gid=1993687
pdz15_gid=cat_id_row(pdz15_match_old,gid,'ID2008')
pdzv2_gid=cat_id_row(pdzv2_match_old,gid,'ID')
keys15=pdz15_g.keys() ;keysv2 = pdzv2_g.keys()
s15=set(keys15)
sv2=set(keysv2)
set.intersection(s15,sv2)
bothkeys=set.intersection(s15,sv2)
for k in bothkeys:
	kk.append(pdz15_g[k] == pdzv2_g[k])

bothkeys=list(bothkeys)
bothkeys_ar=array(bothkeys)
bothkeys_ar=numpy.array(bothkeys)
kk=[]
for k in bothkeys:kk.append(pdz15_g[k] == pdzv2_g[k])
kk_ar=numpy.array(kk)
bothkeys_ar[kk_ar]
bothkeys_ar[logical_not(kk_ar)]
bothkeys_ar[numpy.logical_not(kk_ar)]
nonsame=bothkeys_ar[numpy.logical_not(kk_ar)]
for k in nonsame:
    print k, pdz15_g[k], pdzv2_g[k]

