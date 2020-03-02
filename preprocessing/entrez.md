# Entrez Brainstorm
## Query runs
Use esearch with query parameters and generate a list of runs to download (txt file)
(try something like this) 
	esearch -db gene -query "tp53[preferred symbol] AND human[organism]"

## Downloading data
Use prefetch command with a txt file containing run ids to download
	prefetch --option-file SraAccList.txt

## Get xml with info for query
	esearch -db sra -query "rna-seq[strategy] AND homo sapiens[organism]" | esummary


