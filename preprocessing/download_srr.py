"""
Command for queries:
	esearch -db sra -query "rna-seq[strategy] AND homo sapiens[organism]"
Pipe above into efetch:
	efetch -db sra -format docsum
Above will generate xml with info for query matches.
"""

import os
import subprocess
def main():
	with open('result.xml', "wb") as xml:
		query = "rna-seq[strategy] AND homo sapiens[organism]"
		command =  "esearch -db sra -query".split()
		command.append(query)

		xml.write(subprocess.check_output(command))

if __name__ == '__main__':
	main()

