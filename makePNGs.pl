#!/usr/bin/perl -w
###################
# @file makePNGs.pl
# @author Douglas Applegate
# @date 7/9/2008
#
# @brief Converts all fits file in a dir to jpgs
###################

#$CVSID = "$Id: makePNGs.pl,v 1.1 2008-07-09 21:33:11 dapple Exp $"

##################

use ds9xpautils;
use BonnLogger;

log_force_start;

$usage = "

makePNGs.pl dir [-o outdir]

   Converts all fits files in dir to pngss

   -o  specify output directory for pngss
   
   Make sure the xpa commands {i.e. xpaset, xpaget} are on your path!
";

use File::Basename;
use Getopt::Std;


my %Options;
getopts('ho:', \%Options);

defined($Options{'h'}) and die $usage;

$doCloseDS9 = 0;

defined($ARGV[0]) || die $usage;
$inputDir = $ARGV[0];

$outputDir = $inputDir;
if (defined($Options{'o'})){
    $outputDir = $Options{'o'};
}

@images = glob "$inputDir/*.fits";
while ($file = pop @images){
    doFile($file);
}


&closeDS9;

log_status_and_exit(0);

#############################################################################

sub doFile  {

    local($imagename) = @_;

    my ($base,$path,$type) = fileparse($imagename, '\.fits');

    print "Processing $base...\n";

    &openDS9;
    
    &openDS9Image($imagename);
	
    &saveDS9PNG("$outputDir/$base.png");

}

#############################################################################



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
