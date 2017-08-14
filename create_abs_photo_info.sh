#!/bin/bash 
#. BonnLogger.sh
#. log_start
# script to estimate absolute photometric
# calibration on a night basis. It substitutes
# the old create_photoinfo.sh script.

# $1 main dir
# $2 standard dir
# $3 science dir
# $4 image extension 
# $5 filter
# $6 filter name in standardstar catalog
# $7 color index (e.g. VmI)
# $8 Extinction for fits with constant extinction
# $9 color for fit with constant color term
# $10 lower limit for magnitudes to be considered
#     (standard star catalog) (OPTIONAL argument;
#      set to 0.0 by default)

# 03.11.2004 Filter measured magnitudes for nonsense
#
# 25.11.2004:
# we adapted the script to the new output of fitsort
# that no longer gives the file including the whole
# but only the filename.
#
# 07.12.2004:
# I corrected a bug in the writing of ZP and COEFF
# keyowrds (FITS standard issues)
#
# 10.12.2004:
# Now passes the new label argument to phot_abs.py
#
# 26.02.2005:
# I introduced a new argument to account for a different
# 'filter' name and the name for that filter in the standard
# star catalog.
#
# 01.03.2005:
# I introduced temporary output files for files created
# by photo_abs.py. photo_abs.py uses pgplot that cannot
# handle too long file names.
#
# 11.03.2005:
# We now write all photometric solutions to the header.
# In case the night was estimated non-photometric the
# ZPCHOICE keyword 0
#
# 13.03.2005:
# In the header updates the next free dummy keyword is
# now searched automatically. This part is written more
# modular now.
#
# 17.03.2005:
# If the night is marked as non-photometric, ZPCHOICE is
# set to 0 now.
#
# 19.03.2005:
# I corrected a syntax error in an if statement (that probably
# was introduced in one of the last commits)
#
# 14.08.2005:
# The call of the UNIX 'sort' program is now done
# via a variable 'P_SORT'.
#
# 05.12.2005
# Chips whose NOTUSE or NOTPROCESS flag is set are not
# considered in the determination of absolute photometric
# zeropoints.
#
# 23.01.2006:
# I introduced a new command line argument giving the minimum 
# magnitude for standard stars to be considered. This argument
# is optional. This change should help to better reject bright
# objects with saturated features.

. ${INSTRUMENT:?}.ini
. bash_functions.include

if [ $# -eq 10 ]; then
  MINMAG=${10}
else
  MINMAG=0.0
fi

if [ ! -d "/$1/$2/calib" ]; then
  mkdir /$1/$2/calib
fi

# find the chip catalogs that should be used for photometry,
# i.e. reject chips that have the NOTUSE flag set.

CATS=""
i=1
while [ ${i} -le ${NCHIPS} ]

#while [ ${i} -le 8 ]
do
  if [ ${NOTUSE[${i}]:=0} -eq 0 ] && [ ${NOTPROCESS[${i}]:=0} -eq 0 ]; then
      CATS="${CATS}  /$1/$2/cat/chip_${i}_merg.cat"
  fi
  i=$(( $i + 1 ))
done
${P_LDACPASTE} -i ${CATS} -t PSSC\
               -o ${TEMPDIR}/tmp_chips_$$.cat


${P_LDACFILTER} -i ${TEMPDIR}/tmp_chips_$$.cat -t PSSC\
                -c "(((${6}mag < 99) AND ($7 < 99)) AND (Mag < 0))AND(${6}mag > ${MINMAG});"\
                -o /$1/$2/cat/allchips_merg.cat




${P_LDACFILTER} -i /$1/$2/cat/allchips_merg.cat -t PSSC\
                -c "($7 > -10) AND ($7 < 10);"\
                -o /$1/$2/cat/allchips_tmp.cat





LABEL=`echo $7 | sed 's/m/-/g'`

# Create a FIFO
mkfifo ${TEMPDIR}/nights_$$.asc

# Get a list of all nights and write it to the FIFO
${P_LDACTOASC} -i /$1/$2/cat/allchips_tmp.cat  -t PSSC\
    -b -k GABODSID | ${P_SORT} | uniq > ${TEMPDIR}/nights_$$.asc &

echo  ${TEMPDIR}/nights_$$.asc 
# fd=0: FIFO, fd=3: TTY

i=0
vo=''
#cat ${TEMPDIR}/nights_$$.asc |
cp ${TEMPDIR}/nights_$$.asc ${TEMPDIR}/nightscopy_$$.asc 
declare -a nightslist
while read ni 
do
	nightslist[$i]="$ni"
	let i=i+1
done < ${TEMPDIR}/nightscopy_$$.asc 
echo ${nightslist[*]} 

#exec 4<&0 < ${TEMPDIR}/nights_$$.asc
SIGMAOK=1
SIGMAREJECT=1.2


#exec 3<&0 < ${TEMPDIR}/nights_$$.asc
echo ${nightslist[*]} 
#while read NIGHT
for NIGHT in ${nightslist[*]}
do
    echo $NIGHT
    echo ${nightslist[*]} 
    SIGMAOK=1
    while [ ${SIGMAOK} -eq 1 ] 
    do
       	echo ${NIGHT}
		echo "       ---==== Calibrating night ${NIGHT} ====---"
        echo
        ${P_LDACFILTER} -i /$1/$2/cat/allchips_tmp.cat  -t PSSC\
	    -o /$1/$2/cat/night_${NIGHT}.cat -c "(GABODSID=${NIGHT});"
        ${P_LDACTOASC} -i /$1/$2/cat/night_${NIGHT}.cat  -t PSSC\
	    -b -k Mag ${6}mag ${7} AIRMASS | sort | uniq > ${TEMPDIR}/night_$5_${NIGHT}_$$.asc
		# added a new filter to get rid of duplicates, the sort | uniq filter
	    #-b -k Mag ${6}mag ${7} AIRMASS OBS_NAME IMAGEID Ra Dec > ${TEMPDIR}/night_$5_${NIGHT}_$$.asc
               
        echo "./photo_abs.py --input=${TEMPDIR}/night_$5_${NIGHT}_$$.asc \
	    --output=${TEMPDIR}/photo_res --extinction="$8" \
	    --color="$9" --night=${NIGHT} --label=${LABEL} --sigmareject=${SIGMAREJECT}"
                                                                                       
        ./photo_abs.py --input=${TEMPDIR}/night_$5_${NIGHT}_$$.asc \
	    --output=${TEMPDIR}/photo_res --extinction="$8" \
	    --color="$9" --night=${NIGHT} --label=${LABEL} --sigmareject=${SIGMAREJECT}
                                                                                                      
        mv ${TEMPDIR}/photo_res.asc /$1/$2/calib/night_${NIGHT}_$5_result.asc
        mv ${TEMPDIR}/photo_res.ps /$1/$2/calib/night_${NIGHT}_$5_result.ps
                                                                                                      
        echo 
        echo "Displaying solutions ..."
	    echo ${TEMPDIR}
        echo 
                                                                                                      
        gv /$1/$2/calib/night_${NIGHT}_$5_result.ps &
        GVPID=$!
                                                                                                      
        i=1
        while read -a SOL
        do
	    ZP[$i]=${SOL[0]}
	    COEFF[$i]=${SOL[1]}
	    COL[$i]=${SOL[2]}
	    i=$(($i + 1))
        done < /$1/$2/calib/night_${NIGHT}_$5_result.asc
                                                                                                      
        ZP[$i]=-1.0
        COEFF[$i]=-1.0
		echo
		echo
		echo
    	echo '##########################################' 
		echo "The GABODSID value for this night is ${NIGHT}"
		echo -n "These are the nights included in this run "
		echo ${nightslist[*]}
		echo "Current Sigma Rejection Value is ${SIGMAREJECT}"	
		echo "(-1) Enter a new Simga Rejection value "
        echo "(0) No acceptable solution (not photometric!)"
        echo "(1) 3 Parameter fit"
        echo "(2) 2 Parameter fit"
        echo "(3) 1 Parameter fit"
        echo -n "Choose input and press [ENTER]: "
        # Now read from old stdin/TTY
        read CHOICE #<&3

		SIGMAOK=0
    	if [ ${CHOICE} -eq -1 ]; then
		echo "Enter new Sigma Rejection value "
        read SIGMAREJECT #<&3
		SIGMAOK=1
		fi

    done 
    

    kill ${GVPID} 2>/dev/null

    ZPCHOICE=${CHOICE}
    #
    # the 'solution' -1.0 for the zeropoint,
    # i.e. the night was marked nonphotometric
    # is stored in the last array element. Hence,
    # this case needs special treatment as in
    # the interactive setup this is choice '0'.
    if [ ${CHOICE} -eq 0 ]; then
	CHOICE=$i
	ZPCHOICE=0
    fi

    echo
    echo "Updating image headers ..."
    echo

    ${P_DFITS} /$1/$3/*$4.fits | ${P_FITSORT} -d GABODSID | \
	${P_GAWK} '{if ($2 == '${NIGHT}') print $1}' > ${TEMPDIR}/night_${NIGHT}_img_list_$$.asc

    #python record_photometry.py $BONN_TARGET $BONN_FILTER $username $ZPCHOICE $ZP1 $COLOR1 $AIRMASS1 $ZP2 $COLOR2 $AIRMASS2 $ZP3 $COLOR3 $AIRMASS3 errors

    while read IMG
    do
	echo $IMG
	# Write the choice to the header

	value ${ZPCHOICE}
	writekey /$1/$3/${IMG} ZPCHOICE "${VALUE}" REPLACE

	value ${ZP[$CHOICE]}
	writekey /$1/$3/${IMG} ZP "${VALUE}" REPLACE

	value ${COEFF[$CHOICE]}
	writekey /$1/$3/${IMG} COEFF "${VALUE}" REPLACE

	value ${COL[$CHOICE]}
	writekey /$1/$3/${IMG} COLCOEFF "${VALUE}" REPLACE

	i=1
	while [ "${i}" -le "3" ]
        do
	  value ${ZP[$i]}
	  writekey /$1/$3/${IMG} ZP${i} "${VALUE}" REPLACE

	  value ${COEFF[$i]}
	  writekey /$1/$3/${IMG} COEFF${i} "${VALUE}" REPLACE

	  value ${COL[$i]}
	  writekey /$1/$3/${IMG} COLCOEFF${i} "${VALUE}" REPLACE

	  i=$(( $i + 1 ))
	done

    done < ${TEMPDIR}/night_${NIGHT}_img_list_$$.asc

done 

# Restore old stdin, close fd=3
#exec <&3 3<&- 

#rm ${TEMPDIR}/nights_$$.asc ${TEMPDIR}/night_$5_*_$$.asc \
#    ${TEMPDIR}/night_*_img_list_$$.asc ${TEMPDIR}/tmp_chips_$$.cat
#log_status $?
