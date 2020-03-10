# streaming and piping functions
## usage: compile with `g++ stream_kmers.cpp -o stream_kmers`.
## On its own, stream_kmers takes two parameters: the first parameter is the k value and the second paramter is the maximum number of reads to count. Next functionality to implements is an auto-stopping based on convergence of kmer-count frequency.

## In a pipeline, usage looks like this: `fastq-dump --skip-technical --split-spot -Z SRR5149059 | ./stream_kmers 6 100 > out.txt` to count k=6 and with a limit of 100 reads.