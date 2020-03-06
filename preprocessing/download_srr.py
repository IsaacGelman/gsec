import os
import subprocess
import xml.etree.ElementTree as ET

def main():
	filename = input("Enter name of the xml file: ")
	tree = ET.parse(filename)
	root = tree.getroot()
	
	# iterate over xml tree and get SRRs
	srrs = []
	for runs in root.iter('Runs'):
		for run in runs.iter('Run'):
			srrs.append(run.attrib['acc'])

	# write srrs to txt file
	message = "Found {} SRRs, how many would you like to download?".format(len(srrs))
	n = int(input(message))
	
	with open('srr_list.txt', 'w') as txt:
		for i in range(n):
			txt.write(srrs[i]+'\n')

	

				
if __name__ == '__main__':
	main()

