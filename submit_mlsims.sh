#!/bin/bash
#set -xv

simdir=$1
filterset=$2
priority=$3

#subarudir=/nfs/slac/g/ki/ki05/anja/SUBARU
#adam-old# for filterset in `cat cosmos_combos.txt`; do

maindir=`\ls -d ${simdir}/${filterset}/ `
workdirs=`\ls -d ${simdir}/${filterset}/*/ `
for workdir in $workdirs
do

	for sim in $workdir/cutout*.cat; do

	    simbase=`basename $sim .cat`

	    z=`echo $simbase | awk -F'_' '{print $4}' | awk -F'=' '{print $2}'`
	    mass=`echo $simbase | awk -F'_' '{print $5}'| awk -F'=' '{print $2}'`
	    iter=`echo $simbase | awk -F'_' '{print $6}'`

	    logfile=$workdir/nocontam/maxlike/$simbase.log

	    if [ ! -e $workdir/nocontam/maxlike ]; then

		mkdir -p $workdir/nocontam/maxlike
	    fi

	    if [ -e $logfile ]; then

		isSuccess=`grep Success $logfile`
		if [ -n "$isSuccess" ];then

		continue
		fi

		rm $logfile

	    fi

	    echo $filterset $z $mass $iter

	    outfile=$workdir/nocontam/maxlike/$simbase.out
	    
	    jobfile=simqueue/p$priority.$filterset.$z.$mass.$iter.sim

	    echo "#!/bin/bash" > $jobfile
	    
	    echo "bsub -W 9 -R rhel60 -m bulletfarm -oo $logfile  ./maxlike_simdriver.py -o $outfile -i $sim -p $maindir/pdz.pkl -b $maindir/bpz.cat" >> $jobfile
	    
	    chmod a+x $jobfile
		
	done

done
