#!/usr/bin/perl -w
#####################

$limit=4;
$nargs=@ARGV;
print "${nargs}\n";
if ($nargs > 0) {
    $limit = $ARGV[0];
}
$sleep_period = 10; #seconds

print "Job limit: $limit\n";


while ($job = <STDIN>) {

    @batchargs = split(/ /, $job);
    $cluster=$batchargs[0];
    $filter=$batchargs[1];

    print "Submitting $cluster $filter \n";
    
    $njobs=`bjobs | wc -l`;
    
    while ($njobs >= $limit){
	sleep $sleep_period;
	$njobs=`bjobs | wc -l`;
    }

    system("./submit_coadd_batch2.sh $cluster 'all' $filter");

    sleep $sleep_period;
}
