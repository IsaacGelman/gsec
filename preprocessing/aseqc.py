#!/usr/bin/python

import os
import subprocess import xml.etree.ElementTree as ET
import sys 


"""
Arguments:
1) positive (string)
2) negative (string)

Obs: expecting input like "strategy_organism" for positive and negative strings
If there are spaces in a word, separate with "-"

Obs2: Implement better arguments with getopt module later
"""
def main(argv):
	# Get positive and negative strings
	pos = argv[1]
	neg = argv[2]
	
	# get xml result into temp file
	pos_strat, pos_org = pos.split('_')[0], pos.split('_')[1]
	neg_strat, neg_org = neg.split('_')[0], neg.split('_')[1]
	
	pos_query = "esearch -db sra '{}[strategy] AND {}[organism]' | efetch -db sra -format docsum > {}".format(pos_strat, pos_org, 'pos.xml')
	
	neg_query = "esearch -db sra '{}[strategy] AND {}[organism]' | efetch -db sra -format docsum > {}".format(neg_strat, neg_org, 'neg.xml')
	os.system(pos_query)
	os.system(neg_query)

	# get srrs
	pos_srrs = parse_xml('pos.xml', 5)
	neg_srrs = parse_xml('neg.xml', 5)

	# delete temp srr files
	os.system('rm pos.xml, neg.xml')
	
	# download files
	print("Downloading positive...")
	for srr in pos_srrs:
		os.system('srapath {} | wget').format(srr)
	for srr in neg_srrs:
		os.system('srapath {} | wget').format(srr)

	return 0
	
	

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
