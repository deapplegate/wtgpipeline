#!/bin/bash
set -xv
#adam-does# copied from process_science_4channels_eclipse_para.sh

#$1: main directory (filter)
#$2: Bias directory
#$3: Flat directory
#$4: Science directory
#$5: RESCALE/NORESCALE
#$6: FRINGE/NOFRINGE
#$7: chips to be processed

# preliminary work:
. ${INSTRUMENT:?}.ini > /tmp/instrum.out 2>&1

# the resultdir is where the output coadded images
# will go. If ONE image of the corresponding chip
# is a link the image will go to THIS directory
for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    RESULTDIR[${CHIP}]="$1/$4"
  else
    echo "Chip ${CHIP} will not be processed in $0"  
  fi
done


for CHIP in $7
do
  if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    if [ "${RESULTDIR[${CHIP}]}" != "$1/$4" ]; then
       ln -s ${RESULTDIR[${CHIP}]}/$4_${CHIP}.fits $1/$4/$4_${CHIP}.fits
    fi
  
    # do statistics from all science frames.
    # This is necessary to get the mode
    # of the combination from all images, so that
    # the combination where images have been excluded
    # can be scaled accordingly.
    ${P_IMSTATS} `\ls /$1/$4/SUB_IMAGES/*_${CHIP}OCF_sub.fits` \
                 -o science_images_$$
  
    RESULTMODE=`${P_GAWK} 'BEGIN {mean=0.0; n=0} ($1!="#") {
                           n=n+1; mean=mean+$2} END {print mean/n}' science_images_$$`
  
    # modify the input list of images
    # in case we have to reject files for the superflat:
    if [ -s /$1/superflat_exclusion ]; then
      ${P_GAWK} 'BEGIN {nex = 0; while (getline <"/'$1'/superflat_exclusion" > 0) {
                 gsub(" ", "", $1); if (length($1) >0) {ex[nex]=$1; nex++; }}}
                 {exclude = 0; i=0;
                  while (i<nex) {
                    if ((ind=index($1, ex[i]))!=0) {
                      tmp=$1;
                      gsub(ex[i],"",tmp);
                      first=substr(tmp,ind,1);
                      if (first !~ /[0-9]/) {
                        exclude = 1;
                      }
                    }
  	          i++;
                  }
                  if(exclude == 0) {print $0}}' science_images_$$ > science_coadd_images_$$
    else
      cp science_images_$$ science_coadd_images_$$
    fi
  
    # do the combination
  
    #make SCIENCE_#.fits
    ${P_IMCOMBFLAT_IMCAT} -i science_coadd_images_$$\
                    -o ${RESULTDIR[${CHIP}]}/$4_${CHIP}.fits \
                    -s 1 -e 0 1 -m ${RESULTMODE}
  

  fi
done


#adam-BL# log_status $?

rm -f science_images_$$ science_coadd_images_$$ images-objects_$$
