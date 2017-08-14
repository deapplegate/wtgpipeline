#!/usr/bin/perl -w

# update_preprocess.pl file

open(TEMPLATE, 'do_Subaru_preprocess_template.sh');
@temp = ();
$read = 0;
while ($line = <TEMPLATE>){
    if ($read == 1){
	push(@temp, $line);
    }
    
    if ($line =~ /#Comment out/){
	$read = 1;
    }
}

close(TEMPLATE);

$nfiles = @ARGV;

for ($i=0; $i < $nfiles; $i+=1) {
    $file = $ARGV[$i];
    open(INPUT, $file);
    @in = ();
    while ($line = <INPUT>){
	push(@in, $line);
	
	if ($line =~ /#Comment out/){
	    last;
	}
    }
    close(INPUT);

    open(OUTPUT, "> $file");
    foreach $line (@in){
	print OUTPUT "$line";
    }
    foreach $line (@temp){
	print OUTPUT "$line";
    }
    close(OUTPUT);
}
