#!/usr/bin/perl -w

use constant PI => 4*atan2(1,1);

$outputname = $ARGV[0];

open(OUTPUT, " > $outputname");

#$ngalsperbin = 80;
$galalpha = 6e-7;
$galbeta = 6.3;

$xmin = 0;
$xmax = 12000;
$ymin = 0;
$ymax = 12000;

$magmin = 20;
$magmax = 28;
#$types = qw(expdisk devauc);
$minrh = 2;
$maxrh = 10;

$totalgals = 0;



$type="expdisk";
#for ($mag = $magmin; $mag <= $magmax; $mag += 2){
#
#    for ($rh = $minrh; $rh <= $maxrh; $rh += 4){
#	
#	for ($ellip = .1; $ellip < .4; $ellip += .2){
#
#	    $ratio = sqrt(1 - $ellip);
#
#	    print "$type $mag $rh $ratio\n";
#	    $ngalsperbin = $galalpha*($mag**$galbeta);
#	    $totalgals += $ngalsperbin;
#	    for ($i=0; $i < $ngalsperbin; $i+=1){
#		$x = rand($xmax - $xmin) + $xmin;
#		$y = rand($ymax - $ymin) + $ymin;
#		$phi = rand(360);
#
#		print OUTPUT "$x $y $mag $type $rh $ratio $phi\n"
#	    }
#
#	} 
#	
#    }
#
#}
#
for ($mag = $magmin; $mag <= $magmax; $mag += 1){

    $ellip = 0;

    for ($rh = 2.5; $rh <= 5; $rh += 2.5){
	
	$ratio = sqrt(1 - $ellip);
	
	print "$type $mag $rh $ratio\n";
	
	$ngalsperbin = $galalpha*($mag**$galbeta);
	$totalgals += $ngalsperbin;
	for ($i=0; $i < $ngalsperbin; $i+=1){
	    
	    $x = rand($xmax - $xmin) + $xmin;
	    $y = rand($ymax - $ymin) + $ymin;
	    $phi = rand(360);

	    print OUTPUT "$x $y $mag $type $rh $ratio $phi\n"
	}
	
    } 
	
}


$type="devauc";
for ($mag = $magmin; $mag < $magmax; $mag += 3){

    $ellip = 0;

    for ($rh = 2.5; $rh <= 5; $rh += 2.5){
	
	$ratio = sqrt(1 - $ellip);
		    
	print "$type $mag $rh $ratio\n";
	$ngalsperbin = $galalpha*($mag**$galbeta);
	$totalgals += $ngalsperbin;
	for ($i=0; $i < $ngalsperbin; $i+=1){
	    $x = rand($xmax - $xmin) + $xmin;
	    $y = rand($ymax - $ymin) + $ymin;
	    $phi = rand(360);
	    print OUTPUT "$x $y $mag $type $rh $ratio $phi\n"
	}
	
    } 

}

print "Total galaxies: $totalgals";
close OUTPUT;
