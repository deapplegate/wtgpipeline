#!/usr/bin/perl -w
####################################
# Works with DS9 via XPA to draw lines, mark rows or columns, and draw boxes.
####################################

#CVSID = "$Id: mark_badpixel_regions.pl,v 1.5 2009-02-27 22:32:49 dapple Exp $";

##########################################

use File::Basename;
use Cwd 'abs_path';
use List::Util qw[min max];
use ds9xpautils;
use BonnLogger;

log_force_start;

$usage = "
mark_badpixel_regions.pl image <output>
   image  file to mask into IRAF format
   output output IRAF format region file, optional
\n";

if (scalar(@ARGV) < 1 or scalar(@ARGV) > 2 or $ARGV[0] eq '-h'){
    print $usage;
    log_status_and_exit(1, "Bad usage");
}

$image = abs_path($ARGV[0]);
print "$image\n";
if (scalar(@ARGV) == 3){
    $outfile = $ARGV[1];
} else {
    ($base, $path, $suffix) = fileparse($image,'\.fits');
    $outfile = "$path/$base.imask";
}

&openDS9;

&openDS9Image($image);

$options = "
  (1) Mark Row/Column
  (2) Draw Line
  (3) Draw Box
  (q) quit
";

print "Opening $outfile\n";
open(IRAF, "> $outfile") || die "Cannot open $outfile\n";

while (1) {

    print $options;
    $choice = &promptUser("Enter Choice");

    if ($choice eq '1'){
	&doRowCol;
    } elsif ($choice eq '2') {
	&doLine;
    } elsif ($choice eq '3') {
	&doBox;
    } elsif ($choice eq 'q') {
	last;
    } else {
	print "Enter Valid Choice.\n";
    }
};

close IRAF;
&closeDS9;
log_status_and_exit(0);

################################

sub doRowCol {

    print "Row/Column Selection: Select Point In DS9\n";
    my @point = &readPoint;
    my $dir = &promptUser('(r)ow or (c)ol');


    my @imageSize = split(/ /, &trim(`xpaget ds9 fits size`));
    
    my $line = "";
    my @irafx = ();
    my @irafy = ();
    if ($dir eq 'r') {
	$line = "line(0,$point[1],$imageSize[0],$point[1])";
	@irafx = (0, $imageSize[0]);
	@irafy = ($point[1], $point[1])
    }
    else {
	$line = "line($point[0],0,$point[0],$imageSize[1])";
	@irafx = ($point[0], $point[0]);
	@irafy =(0,$imageSize[1]);
    }

    &addRegion($line);
    &addIRAF(\@irafx, \@irafy);
   
}

##################################

sub doLine {

    print "Line: Select Start\n";
    my @start = &readPoint;
    print "Line: Select Stop\n";
    my @stop = &readPoint;

    my $line = "line($start[0],$start[1],$stop[0],$stop[1])";
    my @irafx = ($start[0], $stop[0]);
    my @irafy = ($start[1], $stop[1]);

    &addRegion($line);
    &addIRAF(\@irafx, \@irafy);

}

##################################

sub doBox {

    print "Box: Select Top Left\n";
    my @corner1 = &readPoint;
    print "Box: Select Bottom Right\n";
    my @corner2 = &readPoint;

    @center = ( ($corner1[0] + $corner2[0])/2., ($corner1[1] + $corner2[1])/2.);
    @size = ($corner2[0] - $corner1[0], $corner2[1] - $corner1[1]);

    my $box = "box($center[0],$center[1],$size[0],$size[1],0)";
    my @irafx = ($corner1[0], $corner2[0]);
    my @irafy = ($corner2[1], $corner1[1]);

    &addRegion($box);
    &addIRAF(\@irafx, \@irafy);

}

##################################

sub readPoint {
    map(&mapRound, split(/ /, &trim(`xpaget ds9 imexam coordinate image`)));
}

##################################

sub addRegion {

    my $region = shift;
    open(OUTPUT, "| xpaset ds9 regions");

    print OUTPUT $region, "\n";

    close OUTPUT;

}

###################################

sub addIRAF {

    my ($xref, $yref) = @_;
    @sortedx = sort {$a <=> $b} @$xref;
    @sortedy = sort {$a <=> $b} @$yref;
    $region = "@sortedx @sortedy";
    print $region, "\n";
    print IRAF $region, "\n";

}

#############################################################################


sub promptUser {

   #CODE FROM http://www.devdaily.com/perl/edu/articles/pl010005/pl010005.shtml
   #-------------------------------------------------------------------#
   #  two possible input arguments - $promptString, and $defaultValue  #
   #  make the input arguments local variables.                        #
   #-------------------------------------------------------------------#

   local($promptString,$defaultValue) = @_;

   #-------------------------------------------------------------------#
   #  if there is a default value, use the first print statement; if   #
   #  no default is provided, print the second string.                 #
   #-------------------------------------------------------------------#

   if ($defaultValue) {
      print $promptString, " [default=", $defaultValue, "]: ";
   } else {
      print $promptString, ": ";
   }

   $| = 1;               # force a flush after our print
   $_ = <STDIN>;         # get the input from STDIN (presumably the keyboard)


   #------------------------------------------------------------------#
   # remove the newline character from the end of the input the user  #
   # gave us.                                                         #
   #------------------------------------------------------------------#

   chomp;

   #-----------------------------------------------------------------#
   #  if we had a $default value, and the user gave us input, then   #
   #  return the input; if we had a default, and they gave us no     #
   #  no input, return the $defaultValue.                            #
   #                                                                 # 
   #  if we did not have a default value, then just return whatever  #
   #  the user gave us.  if they just hit the <enter> key,           #
   #  the calling routine will have to deal with that.               #
   #-----------------------------------------------------------------#

   if ($defaultValue) {
      return $_ ? $_ : $defaultValue;    # return $_ if it has a value
   } else {
      return $_;
   }
}

##############################

sub trim($)
{
	my $string = shift;
	$string =~ s/^\s+//;
	$string =~ s/\s+$//;
	return $string;
}


##############################

sub mapRound{
    my $number = $_;
    return int($number + .5 * ($number <=> 0));
}
