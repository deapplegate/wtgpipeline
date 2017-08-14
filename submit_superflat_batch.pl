#!/usr/bin/perl -w
#######################

$workdir = $ARGV[0];
$set = $ARGV[1];
$group = $ARGV[2];

###############################################################



for ($chip=1; $chip <= 10; $chip += 1){
    
    if ( ! -e "$workdir/$set/$group/SCIENCE_$chip.fits" ){

	$cmd = "bsub -R rhel50 -q medium ./make_superflat_batch.sh $workdir/$set/$group $group $workdir/SCIENCE $chip";
    


	print "$cmd\n";
	system($cmd);
    }

}




