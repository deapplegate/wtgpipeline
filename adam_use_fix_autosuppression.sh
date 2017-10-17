#!/bin/bash
set -xv
#/nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/mask_stars/bright_stars_rings.reg
#/nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/mask_stars/bright_stars_rings_SUPA125912_star1.reg
for ocfr in `\ls -1 /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/SUPA*OCFR.fits | tail -n 99 `
do
	base=`basename $ocfr OCFR.fits`
	ocf="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC_2010-11-04/SCIENCE/${base}OCF.fits"
	reg_fl="/nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/autosuppression/${base}.reg"
	ic '%1 %2 -' $ocf $ocfr > /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/ocf_minus_ocfr_ims/${base}OCF-OCFR.fits
	cp /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/mask_stars/bright_stars_rings.reg /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/autosuppression/${base}.reg
	echo "ds9 -zscale -zoom to fit -cmap bb /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/ocf_minus_ocfr_ims/${base}OCF-OCFR.fits -regions load /nfs/slac/g/ki/ki18/anja/SUBARU/MACS0416-24/W-C-RC/SCIENCE/autosuppression/${base}.reg -zoom to fit " >> ~/bonnpipeline/ds9er.log
done


