#!/bin/bash -xv
. BonnLogger.sh
. log_start
. ${INSTRUMENT:?}.ini

# this script performs astrometry by using astrometrix 

# 23.05.2003:
# added the functionality of 'rename_astrometrixhead.sh'
# to this script
#
# 14.06.2003:
# update of the script to work with version 1.1b of
# the WIFIX package
#
# 23.01.2004:
# we now use the same catalogs as in the singleastrom
# script here in the 'initk' astrometrix step.
# The LDAC catalogs from singleastrom are just linked
# to the appropiate place and hence they do not need to
# be recreated here.
#
# 28.01.2004:
# the links from the original singleastrom cats are
# now removed at the end of the script. Otherwise
# these catalogs are moved if links are resolved at
# a later stage.
#
# 21.03.2004:
# I set the lintol parameter in the initk step to 10 arcsec.
# (This solved a 'no overlap with standard stars' problem
# in one of the sets) 
#
# 06.04.2004:
# - fixed a bug for deleting the links in astrom/$2
#   directory. To be able to do this we have to change
#   to the astrom directory after copying and renaming
#   the headers
# - I changed back the value of the lintol parameter.
#   The problems arised when running astrometrix
#   on several runs simultaneously. This is now
#   done correctly within the create_astrometrix_run.sh
#   script. 
#
# 30.05.04:
# tempaorary files go to a TEMPDIR directory 
#
# 22.08.2007:
# The executable of SExtractor is set to 'sex_theli' as
# it is called now within the THELI pipeline.

# $1: main dir.
# $2: science dir. (the cat dir is a subdirectory of this)
# $3: extension

# first create the astrometrix filelist:
ls -1 /$1/$2/*$3.fits > ${TEMPDIR}/tmp.asc

if [ -f $2.list ]; then
  rm $2.list 
fi

cat ${TEMPDIR}/tmp.asc |\
{
  while read file
  do
    BASE=`basename ${file}`
    echo $2/${BASE} >> $2.list    
  done
}

DIR=`pwd`

cd /$1/$2/

if [ ! -d "astrom" ]; then
  mkdir astrom
  mkdir astrom/$2
fi

cd astrom

mv ${DIR}/$2.list .

# create links for the catalogs as those have
# already been created for the LDAC astrometric
# solution

cd $2
FILES=`ls /$1/$2/cat/*$3.cat`

for CAT in ${FILES}
do
  BASE=`basename ${CAT} .cat`
  ${P_LDACFILTER} -i ${CAT} -t LDAC_OBJECTS -c "((FLAGS<2)OR(FLAGS=16))AND(B_IMAGE>2.0);" \
                  -o ${BASE}.ldac
#  ln -s ${CAT} ${BASE}.ldac 
done

cd ..

perl ${S_ASTROMETRIX} \
 -initk -s table=$2.dat -s list=$2.list -s fits_dir=$1 -s catalog=USNOB1\
 -s narrow=n -s thresh=10 -s radius=60 -s groupccd=y -s cats_dir="" \
 -s outdir_top=/$1/$2/astrom -s SEX=sex_theli

perl ${S_ASTROMETRIX} \
 -global

cd ..

# finally copy the astrometrix headers to the right place
# and rename them

if [ ! -d "headers" ]; then
  mkdir headers
fi

cp ./astrom/astglob/*head ./headers

cd ./headers

ls *$3.head > ${TEMPDIR}/headernames_$$

cat ${TEMPDIR}/headernames_$$ |\
{
  while read file
  do
    BASE=`basename ${file} $3.head`
    mv ${file} ${BASE}.head
  done
}

cd ../astrom

# clean the astrom/$2 directory from the links
# otherwise catalogs are moved if links are resolved
# at a later stage
cd $2
FILES=`ls *$3.ldac`

for CAT in ${FILES}
do
  if [ -L ${CAT} ]; then
    rm ${CAT}
  fi
done


cd ${DIR}



log_status $?
