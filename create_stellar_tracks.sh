#!/bin/bash -xv

# script to plot Pickles stellar tracks from a colour catalogue
# Plots go to a subdirectory 'stellar tracks' from the first
# argument:

# History information:
# 24.07.2008:
# I removed the command line argument giving all available filters
# for an instrument. It now has to be insured outside this script
# that filters are given in the blue -> red order.
#
# 25.07.2008
# Bug fix: One ldacfilter expression received the wrong command
# line argument.
#
# 20.04.2009
# Each filter must be prefixed with instrument name

#$1: IMDIR
#$2: present filters odered from blue to red! (given in double quotes)
   #     ex SUBARU-8-4-W-J-V MEGAPRIME-0-1-u, etc
#$3: stellar catalog
#$4: magnitude quantity (give in quotes if you want an element from
#    a vector. E.g. give "MAG_APER 10" if you want the tenth element
#    of the MAG_APER key)
#$5: MASK key (optional)

. progs.ini

# Just give a meaningful name to the second argument:
FILTERS="$2"

# disentangle the fith command line argument:
MAGQUANT=`echo $4 | awk '{print $1}'`
MAGINDEX=`echo $4 | awk '{print $2}'` # will be empty if '$4' does not
                                      # contain two elements

if [ "${MAGINDEX}" != "" ]; then
  MAGINDEXCOPY=${MAGINDEX} # necessary because of the "()" 
                           # (special shell characters) appearing
                           # in filenames lateron!!
  MAGINDEX="(${MAGINDEX})"
fi

# get all the filters into an array:
NFILT=0

for FILT in ${FILTERS}
do
    NFILT=$(( ${NFILT} + 1 ))
    FILTER[${NFILT}]=${FILT}
done


test -d $1/stellar_tracks || mkdir $1/stellar_tracks

if [ $# -gt 4 ]; then
    ${P_LDACFILTER} -i $1/$3 -t OBJECTS -c "(${5}<1);"\
      -o ${TEMPDIR}/stellar.cat_$$
    STELLARCAT=${TEMPDIR}/stellar.cat_$$
else
    STELLARCAT=$1/$3  
fi

if [ ${NFILT} -ge 3 ]; then
      # get all possible combinations of three filters
      # and create stellar track plots:
    i=1
    IMAX=$(( ${NFILT} - 2 ))
    JMAX=$(( ${NFILT} - 1 ))
    while [ ${i} -le ${IMAX} ]
    do
        j=$(( ${i} + 1 ))
        k=$(( ${i} + 2 ))
        while [ ${j} -le ${JMAX} ]
        do
            while [ ${k} -le ${NFILT} ]
            do
                echo ${FILTER[${i}]}, ${FILTER[${j}]}, ${FILTER[${k}]}
                ${P_LDACTOASC} -s -b -i ${STELLARCAT} -t OBJECTS \
                    -k "${MAGQUANT}-${FILTER[${i}]}${MAGINDEX}" \
                    "${MAGQUANT}-${FILTER[${j}]}${MAGINDEX}" \
                    "${MAGQUANT}-${FILTER[${k}]}${MAGINDEX}" | \
                    ${P_GAWK} '{print $2-$3,$1-$2}' > \
		    ${TEMPDIR}/stars.asc_$$
		
                ${P_LDACTOASC} -b -i Pickles.cat -t PICKLES \
                    -k ${FILTER[${i}]} > \
		    ${TEMPDIR}/${FILTER[${i}]}.asc_$$
		
		${P_LDACTOASC} -b -i Pickles.cat -t PICKLES \
                    -k ${FILTER[${j}]} > \
		    ${TEMPDIR}/${FILTER[${j}]}.asc_$$

		${P_LDACTOASC} -b -i Pickles.cat -t PICKLES \
                    -k ${FILTER[${k}]} > \
		    ${TEMPDIR}/${FILTER[${k}]}.asc_$$

		paste ${TEMPDIR}/${FILTER[${i}]}.asc_$$ ${TEMPDIR}/${FILTER[${j}]}.asc_$$ ${TEMPDIR}/${FILTER[${k}]}.asc_$$ | ${P_GAWK} '{ print $2-$3,$1-$2}' >\
                        ${TEMPDIR}/pickles.asc_$$
		
		rm ${TEMPDIR}/${FILTER[${i}]}.asc_$$ ${TEMPDIR}/${FILTER[${j}]}.asc_$$ ${TEMPDIR}/${FILTER[${k}]}.asc_$$
		
                FILENAME="$1/stellar_tracks/${FILTER[${i}]}_${FILTER[${j}]}_${FILTER[${k}]}_${MAGQUANT}.eps"
                if [ "${MAGINDEX}" != "" ]; then
                    FILENAME="$1/stellar_tracks/${FILTER[${i}]}_${FILTER[${j}]}_${FILTER[${k}]}_${MAGQUANT}_${MAGINDEXCOPY}.eps"
                fi
		
                {
                    echo 'location 7000 31000 5000 31000'
                    echo 'expand 3'
                    echo 'lweight 3'
                    echo 'term postencap "'${FILENAME}'"'
                    echo 'data "'${TEMPDIR}/'pickles.asc_'$$'"'
                    echo 'read { c1 1 c2 2 }'
                    echo 'limits c1 c2'
                    echo 'data "'${TEMPDIR}/'stars.asc_'$$'"'
                    echo 'read { c1s 1 c2s 2 }'
                    echo 'box'
		    echo 'ctype 0'
                    echo 'ptype 5 2'
                    echo 'expand 1.5'
                    echo 'points c1 c2'
		    echo 'expand 0.5'
                    echo 'ptype 20 3'
		    echo 'ctype red'
                    echo 'points c1s c2s'
		    echo 'ctype 0'
                    echo 'lweight 3'
                    echo 'xlabel "'${FILTER[${j}]}'-'${FILTER[${k}]}'"'
                    echo 'ylabel "'${FILTER[${i}]}'-'${FILTER[${j}]}'"'
                    echo 'hardcopy'
                } | ${P_SM}

                k=$(( ${k} + 1 ))
            done
            j=$(( ${j} + 1 ))
            k=$(( ${j} + 1 ))
        done
        i=$(( ${i} + 1 ))
    done
fi


# clean up:
test -f ${TEMPDIR}/stellar.cat_$$ && rm ${TEMPDIR}/stellar.cat_$$
test -f ${TEMPDIR}/stars.asc_$$   && rm ${TEMPDIR}/stars.asc_$$
test -f ${TEMPDIR}/pickles.asc_$$ && rm ${TEMPDIR}/pickles.asc_$$
