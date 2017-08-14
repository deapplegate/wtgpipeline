#!/usr/bin/perl -w


$workdir = $ARGV[0];
$rejectNums = "1 5";
defined($ARGV[1]) and $rejectNums = $ARGV[1];

@files = <$workdir/*.list>;

foreach (@files) {

    if ($_ =~ /(\w+)_(\d+)\.list/){

	$group = $1;
	$chip = $2;

	if (-e "$workdir/$group/${group}_$chip.fits"){
	    next;
	}
	
	$cmd = "bsub -R rhel50 -q medium ./make_flat_batch.sh $workdir $group \"$rejectNums\" $chip";

	print "$cmd\n";
	system($cmd);

    }

}
