#!/bin/bash
echo " FLIPS - lio"
if [ $# -ne 4 ] ; then
  echo " Create a new list with an added string"
  echo " Syntax:  lio list_in list_out pattern string"
  echo " Example: lio @in-imred @out-imred .fits O"
  echo "          ->  name.fits to nameO.fits"       
  exit
fi

sed -e "s|$3|$4.fits|" $1 > $2

exit

