#!/bin/bash
set -xv
sleep 1

echo "dummy0 start"
sleep 1
echo "dummy0 end"
for num in 1 2 3 4 5 
do
	echo $num
done
exit

