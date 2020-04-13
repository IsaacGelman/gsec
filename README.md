# gsec (Generalized Sequencing Classifier)
## pronounced "jee-seek"
### Center for Artificial Intelligence in Society (CAIS++) and Smith Computational Genomics Lab Collaboration.

# Requirements:
1. Entrez utilities (esearch, etc.)
2. SRA toolkit
3. Python 3

# Recommended:
Disable SRA download caching:
1. Follow instructions at https://standage.github.io/that-darn-cache-configuring-the-sra-toolkit.html
2. run vdb-config --interactive
3. go to cache tab and uncheck "enable local file-caching" if it isn't already

# Streaming and piping functions:
usage: compile with `g++ stream_kmers.cpp -o stream_kmers`.

On its own, stream_kmers takes two parameters: the first parameter is the k value and the second paramter is the maximum number of reads to count. Next functionality to implements is an auto-stopping based on convergence of kmer-count frequency.

In a pipeline, usage looks like this: `fastq-dump --skip-technical --split-spot -Z SRR5149059 | ./stream_kmers 6 100 > out.txt` to count k=6 and with a limit of 100 reads. The specific SRR provided is downloaded but never saved and only the counts file is saved. If you already have an `.sra` file you can run it on that as well. Streaming gives a speed boost in both scenarios.

# gsec-train.py usage
This script will query SRRs that match the specified fields and count the kmers up to the specified k value. It will then save count files to a given directory.


`python gsec-train.py --pos-strat --pos-org --neg-strat --neg-org -k -l -o -n`
- pos-strat: strategy for positive set
- pos-org: organism for positive set
- neg-strat: strategy for negative set
- neg-org: organism for negative set
- k: maximum size of kmer to count
- l: limit number of reads to use
- o: directory path to save count files
- n: number of srrs to count for each target (if there are less files that match the query, the maximum amount of files matched will be downloaded)

Example:
`python gsec-train.py --pos-strat rna-seq --pos-org 'homo sapiens' --neg-strat wgs --neg-org 'homo sapiens' -k 3 -l 20 -o 'data/' -n 10
`
