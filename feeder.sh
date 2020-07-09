#!/bin/bash
# Script to feed the 'count' and 'skip' values to the dd command.
# The dd command will extract a small portion of the wiki dump
# Change the name of the python file according to needs

input="/datapartition/surface-names/final/index.txt"
cur=0
prev=0
while read line
do
        prev=$cur
        cur=$line
	if [ $prev -ne 0 ]
        then
	        dd if=/datapartition/enWiki2016/enwiki-20161001-pages-articles-multistream.xml.bz2 of=try1.xml.bz2 bs=1 count=$((cur-prev)) skip=$prev
	        bzip2 -d try1.xml.bz2
	        python3 text-extractor.py
	        rm try1.xml
		echo "scale=2; (($cur*100/14178593313))" | bc -l
	fi
done < "$input"
