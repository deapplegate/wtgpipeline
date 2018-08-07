export SUBARUDIR=/gpfs/slac/kipac/fs1/u/awright/SUBARU/ ; export INSTRUMENT=SUBARU
export bonn=/u/ki/awright/wtgpipeline/
export subdir=/nfs/slac/g/ki/ki18/anja/SUBARU/
#running# ./postH_2009-04-29_W-S-Z+_preprocess_step9.sh 2>&1 | tee -a OUT-postH_2009-04-29_W-S-Z+_preprocess_step9.log
#DONE# ./postH_2009-03-28_W-J-V_preprocess_step9.sh 2>&1 | tee -a OUT-postH_2009-03-28_W-J-V_preprocess_step9.log

## then figure out these ppruns:
##2010-11-04_W-J-B this I re-ran, cause I kinda screwed up and deleted a whole bunch of the SCIENCE/*OCF.fits files
##2010-11-04_W-S-Z+ this I'm holding off on till later. I need to figure out if it can just be run and will process the new stuff without touching the old stuff *(i'm pretty sure this will be fine)

## then do this one and others like it with two flats! (there is a "flatcompare" script if I remember right)
adam-look| mv /nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_W-J-V/SCIENCE_norm /nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_W-J-V/SCIENCE_norm_SKYFLAT
adam-look| #BEFORE moving on to the next step, I'll have to rm SCIENCE and replace it with either SCIENCE_DOMEFLAT or SCIENCE_SKYFLAT!
adam-look| rm -r /nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_W-J-V/SCIENCE/
adam-look| mv /nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_W-J-V/SCIENCE_DOMEFLAT/ /nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_W-J-V/SCIENCE/
adam-look| OR
adam-look| mv /nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_W-J-V/SCIENCE_SKYFLAT/ /nfs/slac/g/ki/ki18/anja/SUBARU/2009-03-28_W-J-V/SCIENCE/

## pick FLAT for these:
2009-09-19_W-J-V/SCIENCE_DOMEFLAT  2010-03-12_W-C-RC/SCIENCE_DOMEFLAT  2010-03-12_W-J-B/SCIENCE_DOMEFLAT  2010-11-04_W-J-B/SCIENCE_DOMEFLAT
2009-09-19_W-J-V/SCIENCE_SKYFLAT   2010-03-12_W-C-RC/SCIENCE_SKYFLAT   2010-03-12_W-J-B/SCIENCE_SKYFLAT   2010-11-04_W-J-B/SCIENCE_SKYFLAT

## to pick SKYFLAT:
ls -d *FLAT
ls SCIENCE_SKYFLAT/
ls DOMEFLAT/ORIGINALS/SUPA*.fits | wc -l
ls SKYFLAT/ORIGINALS/SUPA*.fits | wc -l
rm -r SCIENCE
mv SCIENCE_SKYFLAT SCIENCE
mv DOMEFLAT DOMEFLAT_old
rm -r SCIENCE_DOMEFLAT/ SCIENCE_norm_DOMEFLAT/
mv SCIENCE_norm_SKYFLAT/ SCIENCE_norm
