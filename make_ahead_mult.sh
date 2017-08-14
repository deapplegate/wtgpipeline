#! /bin/bash

#1: input file(s)
#2: output file
#3: MISSCHIPS, e.g. "1 6"

output=${!#}

echo ${output}

echo "first file:" $1
awk '{
      if($1=="CRPIX1" || $1=="CRPIX2" || $1=="CD1_1" || $1=="CD1_2" || $1=="CD2_1" || $1=="CD2_2" || $1=="END") 
         print $0
     }' $1 > ${output}

nlines=`wc ${output} | awk '{print $1}'`

if [ "$#" -ge 2 ]; then
j=2
while [ "$j" -lt "$#" ]
do
file=`echo $* | awk '{print $'${j}'}'`
echo $file
awk '{
      if($1=="CRPIX1" || $1=="CRPIX2" || $1=="CD1_1" || $1=="CD1_2" || $1=="CD2_1" || $1=="CD2_2" || $1=="END") 
         print $0
     }' $file > ${file}.tmp


awk 'BEGIN{
      i=0
      while (i < '${nlines}')
      {
        getline <"'${output}'"
        if ($0 !~ "END")
          old=$3
        getline <"'${file}'.tmp"
        if ($0 !~ "END")
	{
          new=(('${j}'-1)*old + $3)/'${j}'
	  printf("%-8s= %20.9E\n", $1, new)
	}
	else
	  print "END"
	i++
      }
     }' > ${output}.tmp

     mv ${output}.tmp ${output}

j=$(( $j + 1 ))
done
fi

echo "${j} -1 input files"
