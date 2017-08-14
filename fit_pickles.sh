#! /bin/bash -xv

filter=$1

# our magnitudes are all AB. but the SLR expects JHK to be in Vega
ABcorrfilter=0
ABcorrsdss=0
ABcorrblue=0
ABcorrred=0

starcat=pickles.131.cat
startab=SUBARU

case ${filter} in
    "SUBARU-10_2-1-W-J-B" | "SUBARU-10_3-1-W-J-B" | "SUBARU-8-1-W-J-B" | "SUBARU-8-4-W-J-B")
	point1=3
	point2=3
	sdssfit=g
	blue=g
	red=r
    ;;
    "SUBARU-8-2-W-J-B" )
	point1=0.6
	point2=3
	sdssfit=g
	blue=g
	red=r
    ;;
    "SUBARU-10_2-1-W-J-V" | "SUBARU-10_3-1-W-J-V" )
	point1=3
	point2=3
	sdssfit=g
	blue=g
	red=r
    ;;
    "SUBARU-10_2-1-W-S-G+" | "SUBARU-10_1-1-W-S-G+" | "SUBARU-10_3-1-W-S-G+" | "SUBARU-9-1-W-S-G+" | "SUBARU-9-2-W-S-G+" | "SUBARU-9-3-W-S-G+" )
	point1=0.97
	point2=3
	sdssfit=g
	blue=g
	red=r
    ;;
    "SUBARU-10_2-1-W-C-RC" | "SUBARU-10_3-1-W-C-RC" | "SUBARU-8-1-W-C-RC" | "SUBARU-8-2-W-C-RC" | "SUBARU-8-4-W-C-RC" )
	point1=0.44
	point2=1.95
	sdssfit=r
	blue=r
	red=i
    ;;
    "SUBARU-10_2-1-W-S-R+" | "SUBARU-10_1-1-W-S-R+" | "SUBARU-10_3-1-W-S-R+" | "SUBARU-9-1-W-S-R+" | "SUBARU-9-2-W-S-R+" | "SUBARU-9-3-W-S-R+" )
	point1=1.99
	point2=3
	sdssfit=r
	blue=r
	red=i
    ;;
    "SUBARU-10_2-1-W-C-IC" | "SUBARU-10_3-1-W-C-IC" | "SUBARU-8-1-W-C-IC" | "SUBARU-8-2-W-C-IC" | "SUBARU-8-4-W-C-IC" | "SUBARU-9-1-W-C-IC" | "SUBARU-9-2-W-C-IC" | "SUBARU-9-4-W-C-IC" | "SUBARU-9-8-W-C-IC")
#	point1=0.26
#	point2=0.88
#	sdssfit=i
#	sdssblue=i
#	sdssred=z
	point1=3
	point2=3
	sdssfit=i
	blue=r
	red=i
    ;;
    "SUBARU-10_2-1-W-S-I+" | "SUBARU-10_3-1-W-S-I+" )
	point1=1.815
	point1=2
	point2=5
	sdssfit=i
	blue=SUBARU-10_2-1-W-C-RC
	red=SUBARU-10_2-1-W-S-I+
	blue=r
	red=i
    ;;
    "SUBARU-10_2-1-W-S-Z+" | "SUBARU-10_3-1-W-S-Z+" )
	point1=0.9
	point2=5
	sdssfit=z
	blue=SUBARU-10_2-1-W-C-RC
	red=SUBARU-10_2-1-W-S-Z+
	blue=i
	red=z
    ;;
    "MEGAPRIME-0-1-u" )
	point1=1.1
	point2=5
	sdssfit=u
	blue=MEGAPRIME-0-1-u
	red=SUBARU-10_2-1-W-J-B
	blue=u
	red=g
    ;;
    "MEGAPRIME-0-1-g" )
	point1=0.6
	point2=1.4
	sdssfit=g
	blue=MEGAPRIME-0-1-g
	red=SUBARU-10_2-1-W-J-V
	blue=g
	red=r
    ;;
    "MEGAPRIME-0-1-r" )
	point1=1.45
	point2=5
	sdssfit=r
	blue=MEGAPRIME-0-1-g
	red=MEGAPRIME-0-1-r
	blue=g
	red=r
    ;;
    "MEGAPRIME-0-1-i" )
	point1=2
	point2=3
	sdssfit=i
	blue=SUBARU-10_2-1-W-J-V
	red=MEGAPRIME-0-1-i
	blue=r
	red=i
    ;;
    "MEGAPRIME-0-1-z" )
	point1=0.8
	point2=5
	sdssfit=z
	blue=SUBARU-10_2-1-W-C-RC
	red=MEGAPRIME-0-1-z
	blue=i
	red=z
    ;;
    "WHT-U")
	point1=-0.14
	point2=0.47
	sdssfit=u
	blue=g
	red=r
    ;;
    "WHT-B")
	point1=-0.15
	point2=0.25
	sdssfit=g
	blue=g
	red=r
    ;;
    "CFH12K-B")
	point1=0.25
	point2=5
	sdssfit=g
	blue=g
	red=r
        starcat=pickles.cfh12k.cat
        startab=CFH12K
    ;;
    "SPECIAL-0-1-K" )
	point1=7
	point2=9
	sdssfit=Ks
	blue=SUBARU-10_2-1-W-C-RC
	red=SPECIAL-0-1-K
	ABcorrfilter=1.837
	ABcorrsdss=1.844
	ABcorrblue=0
	ABcorrred=1.837
	blue=i
	red=Ks
	ABcorrred=1.844
	# for K, we get the colorterm vs. our R_AB - K_Vega colrterm
    ;;
esac

make_join -i ${starcat} \
          -o pickles.all.cat \
          -m ${startab} \
          -r SDSS \
          -c conf/dummy_SeqNr.mj.conf \
	  -COL_NAME u -COL_INPUT u \
	  -COL_NAME g -COL_INPUT g \
	  -COL_NAME r -COL_INPUT r \
	  -COL_NAME i -COL_INPUT i \
	  -COL_NAME z -COL_INPUT z

# mv pickles.all.cat pickles.tmp.dat
#make_join -i pickles.tmp.cat \
#          -o pickles.all.cat \
#          -m ${startab} \
#          -r 2MASS \
#          -c conf/dummy_SeqNr.mj.conf \
#	  -COL_NAME H  -COL_INPUT H \
#	  -COL_NAME J  -COL_INPUT J \
#	  -COL_NAME Ks -COL_INPUT Ks 

#########################################
#make_join -i Pickles.dwarves.cat \
#          -o pickles.dwarves.tmp.cat \
#          -m PICKLES \
#          -r SDSS \
#          -c conf/dummy_SeqNr.mj.conf \
#	  -COL_NAME u -COL_INPUT u \
#	  -COL_NAME g -COL_INPUT g \
#	  -COL_NAME r -COL_INPUT r \
#	  -COL_NAME i -COL_INPUT i \
#	  -COL_NAME z -COL_INPUT z
#
#make_join -i pickles.dwarves.tmp.cat \
#          -o pickles.dwarves.all.cat \
#          -m PICKLES \
#          -r 2MASS \
#          -c conf/dummy_SeqNr.mj.conf \
#	  -COL_NAME H  -COL_INPUT H \
#	  -COL_NAME J  -COL_INPUT J \
#	  -COL_NAME Ks -COL_INPUT Ks 
#########################################
#
ldactoasc -i pickles.all.cat \
          -t ${startab} \
          -b -k ${filter} ${sdssfit} ${blue} ${red} \
          | awk '{print $1-1*'${ABcorrfilter}', $2-1*'${ABcorrsdss}', $3-1*'${ABcorrblue}', $4-1*'${ABcorrred}'}' \
          | awk '{print $3-$4, $1-$2}' \
	  > /nfs/slac/g/ki/ki05/anja/pickles/${filter}.dat 

cd /nfs/slac/g/ki/ki05/anja/pickles

awk '{if($1>-2 && $1<'${point1}') print $0}' ${filter}.dat > ${filter}_blue.dat
awk '{if($1>'${point1}' && $1<'${point2}') print $0, "0.1"}' ${filter}.dat > ${filter}_red.dat
awk '{if($1>'${point2}' && $1<5) print $0, "0.1"}' ${filter}.dat > ${filter}_vred.dat

~anja/scripts/lin-reg.prog ${filter}_blue.dat > ${filter}_blue.fit
~anja/scripts/lin-reg-err-clip.prog ${filter}_red.dat > ${filter}_red.fit
~anja/scripts/lin-reg-err-clip.prog ${filter}_vred.dat > ${filter}_vred.fit

mblue=`awk '{if($1=="m:") print $2}' ${filter}_blue.fit`
bblue=`awk '{if($1=="b:") print $2}' ${filter}_blue.fit`
#mblue=-0.05

mred=`awk '{if($1=="m:") print $2}' ${filter}_red.fit`
bred=`awk '{if($1=="b:") print $2}' ${filter}_red.fit`

mvred=`awk '{if($1=="m:") print $2}' ${filter}_vred.fit`
bvred=`awk '{if($1=="b:") print $2}' ${filter}_vred.fit`

{
echo 'device postencap "'${filter}'.eps"'
echo "lweight 4"
echo 'data "'${filter}'.dat"'
echo "read { ri 1 rr 2 }"
echo "limits ri rr"
echo "box"
echo "xlabel ${blue}-${red}"
echo "ylabel ${filter} - ${sdssfit}"
echo "ptype 20 3"
#echo "expand 0.3"
echo "points ri rr"
#
echo "ctype blue"
echo 'define l $('${mblue}'*(-2) + 1*'${bblue}')'
echo 'define u $('${mblue}'*('${point1}') + 1*'${bblue}')'
echo 'relocate -2 $l'
echo 'draw "'${point1}'" $u'
#
echo "ctype red"
echo 'define l $('${mred}'*('${point1}') + 1*'${bred}')'
echo 'define u $('${mred}'*('${point2}') + 1*'${bred}')'
echo 'relocate "'${point1}'" $l'
echo 'draw "'${point2}'" $u'
#
echo "ctype magenta"
echo 'define l $('${mvred}'*('${point2}') + 1*'${bvred}')'
echo 'define u $('${mvred}'*(5) + 1*'${bvred}')'
echo 'relocate "'${point2}'" $l'
echo 'draw 5 $u'
#echo "errorbar r g ge 2"
#echo "errorbar r g ge 4"
#echo "relocate (500 31500)"
#echo "label $1/$2"
#echo "relocate (15500 29500)"
#echo "label $3,$4,$5"
#echo "ltype 2"
#echo "relocate 0 0"
#echo "draw 2000 0"
#
echo "hardcopy"
} | sm
