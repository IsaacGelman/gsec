#!/bin/bash
# Usage: ./get_xml.sh strategy organism file.xml
strat=$1
org=$2
filename=$3

esearch -db sra -query "$strat[strategy] AND $org[organism]" | efetch -db sra -format docsum > $3 

