# gsec (_G_eneralized _Se_quencing Classifier) 
## Center for Artificial Intelligence in Society (CAIS++) and Smith Computational Genomics Lab Collaboration.

# Usage:

# Streaming and piping functions:
usage: compile with `g++ stream_kmers.cpp -o stream_kmers`.

On its own, stream_kmers takes two parameters: the first parameter is the k value and the second paramter is the maximum number of reads to count. Next functionality to implements is an auto-stopping based on convergence of kmer-count frequency.

In a pipeline, usage looks like this: `fastq-dump --skip-technical --split-spot -Z SRR5149059 | ./stream_kmers 6 100 > out.txt` to count k=6 and with a limit of 100 reads. The specific SRR provided is downloaded but never saved and only the counts file is saved. If you already have an `.sra` file you can run it on that as well. Streaming gives a speed boost in both scenarios.

# gsec.py usage
This script will query SRRs that match the specified fields and count the kmers up to the specified k value. It will then save count files to a given directory.


`python gsec.py positive_strategy positive_organism negative_strategy negative_organism k lim_reads out_directory num_files`
- positive: class to identify as positive (e.g. rna-seq on homo sapiens)
- negative: class to identify as negative
- k: max kmer to count
- limit: limit of reads per srr
- out_directory: directory to save count files
- num_files: number of srrs to count for each target (if there are less files that match the query, the maximum amount of files matched will be downloaded)

Example:
`python preprocessing.py rna-seq "homo sapiens" wgs "homo sapiens" 6 100 ~/project/data 100`
