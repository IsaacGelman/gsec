#!/usr/bin/python

import os
import subprocess
import xml.etree.ElementTree as ET
import sys 


"""
Usage: python3 full_pipe.py 1 2 3 4 5 6
Arguments:
1) positive strategy (string)
2) positive organism (string)
3) negative strategy (string)
4) negative organism (stirng)
5) max kmer to count (int)
6) limit of reads for each srr (int)

"""
def main(argv):
	# Check arguments
	if len(argv[1:]) != 6:
		print('Usage: ')
		print('python3 aseqc.py pos_strat pos_org neg_strat neg_org')
		return 1


	# Get positive and negative strings
	pos_strat, pos_org = argv[1], argv[2]
	neg_strat, neg_org = argv[3], argv[4]
	k = argv[5]
	limit = argv[6]	

	# Queries
	pos_query = 'esearch -db sra -query "{}[strategy] AND {}[organism]" | efetch -db sra -format docsum > {}'.format(pos_strat, pos_org, 'pos.xml')
	
	neg_query = 'esearch -db sra -query "{}[strategy] AND {}[organism]" | efetch -db sra -format docsum > {}'.format(neg_strat, neg_org, 'neg.xml')
	subprocess.call(pos_query, shell=True)
	subprocess.call(neg_query, shell=True)

	# get srrs
	pos_srrs = parse_xml('pos.xml', 5)
	neg_srrs = parse_xml('neg.xml', 5)

	# delete temp srr files
	os.system('rm pos.xml neg.xml')

	# count srrs
	print("Counting positives...")	
	for srr in pos_srrs:
		count(k, limit, srr)
	print("Counting negatives...")
	for srr in neg_srrs:
		count(k, limit, srr)

	return 0

"""
k (int): max kmer to count
limit (int): limit number of reads to count for given file
srr (str): srr id for read
"""
def count(k, limit, srr):
	# shell commands to run
	fastq = "fastq-dump --skip-technical --split-spot -Z {}"	
	count = "./stream_kmers {} {} > out.txt".format(str(k), str(limit))
	full = fastq + " | " + count
	subprocess.call(full, shell=True)


"""
filename (str): name of xml file to read
n (int): number of srrs to fetch, -1 for all
returns (list[str]): list of SRRs to download
"""
def parse_xml(filename, n):
	tree = ET.parse(filename)
	root = tree.getroot()

	# iterate over xml tree and get SRRs
	srrs = []
	for runs in root.iter('Runs'):
		for run in runs.iter('Run'):
			srrs.append(run.attrib['acc'])
	
	return srrs
	

if __name__ == '__main__':
	main(sys.argv)
