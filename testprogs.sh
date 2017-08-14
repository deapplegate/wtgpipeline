#!/bin/bash
# the script looks in all scripts given on
# the command line whether the programs and
# scripts (script variables with names starting
# with 'S_' or 'P_') are really defined in the
# file 'progs.ini'.
#
# 14.08.2005:
# The call of the UNIX 'sort' program is now done
# via a variable 'P_SORT'.


if  [ ! -f progs.ini ]; then
  echo "file 'progs.ini' not present !!!"
  exit 1
fi

. progs.ini

for script in $@
do
  echo "testing script ${script}:"

  gawk 'BEGIN {FS = "{|}"} 
        {for(i=1;i<NF;i++) {
             if((match($i,"P_")==1) || (match($i,"S_")==1)) {
                print $i}
             }
        }' ${script} | ${P_SORT} | uniq |\
  {
    OK=1
    while read var
    do
      if [ "A_${!var}" == "A_" ]; then
        echo "  Program/Script ${var} undefined !!"
	OK=0
      fi
    done
    if [ "${OK}" == "1" ]; then
	echo "  script ${script} ok!!"
	echo ""
    fi	
  }
  
done

