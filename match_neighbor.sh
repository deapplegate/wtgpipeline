#!/bin/bash -xv

# $1 : output cat
# $2 : table
# $3 : input1 cat
# $4 : input1 cat suffix in final catalog  (ex: e1_{suffix})
# .... continue $2 $3 patter for all catalogs

. progs.ini



TOL=`awk 'BEGIN{print 1.0/3600.}'`  #1 arcsecond search tolerance

build_ssc_args=""
cats=""
let cat_num=-1
for ((i=3;i<$#;i+=2));do
    eval i1=\$$i
    eval i2=\$$((i+1))
    build_ssc_args="$build_ssc_args $i1 $i2"
    cats="$cats $i1"
    let cat_num=cat_num+1
    cats_array[$cat_num]=$i1
    echo ${cats_array[$cat_num]}
done


assoc_input=""
makessc_input=""
filter_input=""
for cat in $cats; do
    ${P_LDACADDKEY} -i $cat \
        -o $cat.assoc \
        -t $2 \
        -k A_assoc ${TOL} FLOAT "" \
        B_assoc ${TOL} FLOAT "" \
        Theta_assoc 0.0 FLOAT "" \
        Flag_assoc 0 SHORT ""

    assoc_input="$assoc_input $cat.assoc"
    makessc_input="$makessc_input $cat.match"
    filter_input="$filter_input $cat.tofilter"
done
echo $makessc_input

#rm $assoc_input $makessc_input make_ssc.conf ${USER}combined.cat
#exit 0;
if [ -e make_ssc.conf ]; then
    rm make_ssc.conf
fi


j=0
for ((i=3;i<$#;i+=2));do
    eval i1=\$$i
    eval i2=\$$((i+1))
    if [ ${i2} == '#' ]; then 
         ldacdesc -i $i1 -t $2 | grep "name" | awk 'BEGIN{FIELDWIDTHS="25 50"}{print "COL_NAME = "$2"\nCOL_INPUT = "$2"\nCOL_MERGE=AVE_REG\nCOL_CHAN="'$j'"\n"}' | sed 's/COL_NAME = SeqNr/COL_NAME = OldSeqNr/g' >> make_ssc.conf
    else
         ldacdesc -i $i1 -t $2 | grep "name" | awk 'BEGIN{FIELDWIDTHS="25 50"}{print "COL_NAME = "$2"_'$i2'\nCOL_INPUT = "$2"\nCOL_MERGE=AVE_REG\nCOL_CHAN="'$j'"\n"}' >> make_ssc.conf
    fi
         
    j=$((j+1))
done


${P_ASSOCIATE} -i $assoc_input \
    -o $filter_input \
    -t $2 \
    -c associate_analyse.conf


echo ${cats_array[$cat_num]}
${P_LDACFILTER} -i ${cats_array[0]}.tofilter -o ${cats_array[0]}.match -c "((Pair_1>0) AND (RICHNESS=2));" -t STDTAB
${P_LDACFILTER} -i ${cats_array[1]}.tofilter -o ${cats_array[1]}.match -c "((Pair_0>0) AND (RICHNESS=2));" -t STDTAB

#${P_LDACFILTER} -i ${cats_array[0]}.tofilter -o ${cats_array[0]}.match -c "((Pair_1>0));" -t STDTAB
#${P_LDACFILTER} -i ${cats_array[1]}.tofilter -o ${cats_array[1]}.match -c "((Pair_0>0));" -t STDTAB


${P_MAKESSC} -i $makessc_input \
         -o /tmp/${USER}combined.cat \
             -t $2 \
         -c make_ssc.conf

ldacrentab -i /tmp/${USER}combined.cat -o $1 -t PSSC $2

#rm $assoc_input $makessc_input make_ssc.conf ${USER}combined.cat
