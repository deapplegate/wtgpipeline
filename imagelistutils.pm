#########################
# @file imagelistutils.pm
# 
# @brief Location of common routines between perl image flipping apps
#########################

#$CVSID = "$Id: imagelistutils.pm,v 1.1 2008-07-10 00:19:11 dapple Exp $";

use Exporter 'import';
@EXPORT = qw(readList readDir promptUser);

############################################################################

sub readList {
    my ($listName) = @_;

    print "List name: $listName\n";

    open(INPUT, $listName) or die "Cannot Open $listName\n";
    my @images = ();
    while ($line = <INPUT>){
	if ($line =~ /^#/){
	    if ($line =~ /^#regiondir:(.+)/ && $regionDir eq ""){
		$regionDir = $1;
		chomp($regionDir);
	    }
	} else {
	    push(@images, $line);
	}
    }
    close(INPUT);

    chomp(@images);

    return @images;
}

#############################################################################

sub readDir {

    my ($dir, $prefix) = @_;

    $dirPath = abs_path("$dir");

    @files = glob "$dirPath/$prefix*.fits";

    return @files;

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


#############################################################################
1;
