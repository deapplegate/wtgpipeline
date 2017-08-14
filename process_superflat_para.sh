#!/bin/bash -u
. BonnLogger.sh
. log_start

###############
# $Id: process_superflat_para.sh,v 1.7 2009-02-10 19:34:42 anja Exp $
###############

# 2009-02-08 (AvdL):
# exposures from which any chip is listed in superflat_exclusion
# are now exluded from the global statistics, since they would
# otherwise bias the result

################
# Takes sub images, and creates superflats

#$1 Run directory
#$2 SCIENCE directory
#$3 CHIPS


# preliminary work:
. ${INSTRUMENT:?}.ini


if [ ! -d $1/$2/SUB_IMAGES ]; then
    mkdir $1/$2/SUB_IMAGES
fi

for CHIP in $3
do
    if [ ${NOTPROCESS[${CHIP}]:=0} -eq 0 ]; then
    # do statistics from all science frames.
    # This is necessary to get the mode
    # of the combination from all images, so that
    # the combination where images have been excluded
    # can be scaled accordingly.
	
	FILES=`ls $1/$2/*_${CHIP}OCF_sub.fits`

	MOVE_SUB=1
	if [ "$FILES" = "" ]; then
	    FILES=`ls $1/$2/SUB_IMAGES/*_${CHIP}OCF_sub.fits`
	    MOVE_SUB=0
	fi

	i=0
	STATFILES=""
	for file in ${FILES}
	do
	  base=`basename ${file} _${CHIP}OCF_sub.fits`
	  exclude=`grep ${base} $1/superflat_exclusion | wc | awk '{print $1}'`
	  if [ ${exclude} -eq 0 ]; then
	      STATFILES="${STATFILES} ${file}"
	      i=$(( $i + 1 ))
	  fi
	done

	echo "Chip ${CHIP}: ${i} stat files"

	${P_IMSTATS} ${STATFILES} -o science_images_$$

	RESULTMODE=`${P_GAWK} 'BEGIN {mean=0.0; n=0} ($1!="#") {
            n=n+1; mean=mean+$2} END {print mean/n}' science_images_$$`

	if [ "$RESULTMODE" = "" ]; then
	    log_status 2 "No ResultMode"
	    exit 2
	fi
	
    # modify the input list of images
    # in case we have to reject files for the superflat:
	if [ -s $1/superflat_exclusion ]; then
	    echo "Reading Superflat_Exclusion"
	    ${P_GAWK} 'BEGIN {nex = 0; while (getline <"'$1'/superflat_exclusion" > 0) {
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
	
	${P_IMCOMBFLAT_IMCAT} -i science_coadd_images_$$ \
            -o $1/$2/${2}_${CHIP}.fits \
            -s 1 -e 0 1 -m ${RESULTMODE}
	
	if [ ! -s $1/$2/${2}_${CHIP}.fits ]; then
	    log_status 5 "Superflat not created"
	    exit 5
	fi

	if [ "$MOVE_SUB" = "1" ]; then
	    mv $1/$2/*_${CHIP}OCF_sub.fits $1/$2/SUB_IMAGES/
	fi
	rm science_images_$$ science_coadd_images_$$
	
    fi
done



log_status $?
