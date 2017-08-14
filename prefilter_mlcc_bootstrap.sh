#!/bin/bash

cluster=$1
filter=$2
image=$3
workdir=$4
incat=$5
outcat=$6


LENSDIR=/u/ki/dapple/subaru/$cluster/LENSING_${filter}_${filter}_aper/$image


case ${filter} in
  "g" | "r" | "i" )
    detectmag=MAG_APER1-MEGAPRIME-COADD-1-${filter} ;;
  * )
    detectmag=MAG_APER1-SUBARU-COADD-1-${filter} ;;
esac

brightcut=`awk '{if($1=="'${detectmag}'" && $2==">" && $4!="AND") print $0}' ${LENSDIR}/cc_cuts3.dat`
flagcut=`awk '{if($1~"IMAFLAGS_lensimage") print $0}' ${LENSDIR}/cc_cuts3.dat`
rhcut=`awk '{if($1=="rh") print $0}' ${LENSDIR}/cc_cuts3.dat`
Pgscut=`awk '{if($1=="Pgs") print $0}' ${LENSDIR}/cc_cuts3.dat`
gscut=`awk '{if($1=="gs") print $0}' ${LENSDIR}/cc_cuts3.dat`
sncut=`awk '{if($1~"snratio") print $0}' ${LENSDIR}/cc_cuts3.dat`
imagcut=`awk '{if(($1=="MAG_APER1-SUBARU-COADD-1-W-S-I+" || $1=="HYBRID_MAG_APER-SUBARU-10_2-1-W-S-I+") && $2=="<") print $0}'  ${LENSDIR}/cc_cuts3.dat | awk '{if(NR==1) print $0}'`


blue=`awk '{if($1~"bluemag") print $2}' ${LENSDIR}/redseq_all.params`
green=`awk '{if($1~"greenmag") print $2}' ${LENSDIR}/redseq_all.params`
red=`awk '{if($1~"redmag") print $2}' ${LENSDIR}/redseq_all.params`
rscut=`awk '{if($1~"('${blue}'-'${green}')") print $0}' ${LENSDIR}/cc_cuts3.dat`

#cuts="(((($brightcut) AND ($flagcut)) AND (($rhcut) AND ($Pgscut))) AND ((($gscut) AND ($sncut)) AND (($imagcut) AND ($rscut))));"

#cuts=(((((((($brightcut)AND($flagcut))AND($rhcut))AND($Pgscut))AND($gscut))AND($sncut))AND($imagcut))AND($rscut));


i=0
curcat=$incat
for cut in "$imagcut" "$sncut" "$brightcut" "$flagcut" "$rhcut" "$Pgscut" "$gscut" "$rscut"; do
    nextcat=$workdir/filtered_$i.cat
    ldacfilter -i $curcat -o $nextcat -t STDTAB -c "($cut);"
    if [ $? -ne 0 ]; then
	exit 1
    fi
    i=$((i+1))
    curcat=$nextcat
done

mv $curcat $outcat

