#!/bin/bash
# Script to feed the 'count' and 'skip' values to the dd command.
# The dd command will extract a small portion of the wiki dump

input="/mnt/d/Experiment/index.txt"
cur=0
prev=0
while read line
do
        prev=$cur
        cur=$line
	if [ $prev -ge 8914543669 ]
        then
	        dd if=enwiki-20200101-pages-articles-multistream.xml.bz2 of=try1.xml.bz2 bs=1 count=$((cur-prev)) skip=$prev
	        bzip2 -d try1.xml.bz2
	        python3 text-extractor.py
	        rm try1.xml
		echo "scale=2; (($cur*100/17751212678))" | bc -l
	fi
done < "$input"
