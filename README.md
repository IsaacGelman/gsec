# gsec (Generalized Sequencing Classifier)
## pronounced "jee-seek"
### USC Center for Artificial Intelligence in Society (CAIS++) and Smith Computational Genomics Lab Collaboration.
                                                                                
# Requirements:
1. Entrez utilities (esearch, etc.)
2. SRA toolkit (fastq-dump in command line should not throw "not found")
3. Python 3
4. After pulling the repo, enter the `gsec/utils` folder in the install location
and type `make` to compile the kmer counting function.
5. Clone the repo, enter the directory, and run `pip install .`

# Highly recommended:
Disable SRA download caching: Follow the instructions at 
https://standage.github.io/that-darn-cache-configuring-the-sra-toolkit.html OR 
run `vdb-config --interactive`; go to the cache tab and uncheck "enable local
file-caching" if it isn't already. 

# Streaming and piping functions:
usage: compile with `g++ stream_kmers.cpp -o stream_kmers`.

On its own, stream_kmers takes two parameters: the first parameter is the
k value and the second parameter is the maximum number of reads to count. 
Next functionality to implement is an auto-stopping based on convergence 
of kmer-count frequency.

In a pipeline, usage looks like this: `fastq-dump --skip-technical \
--split-spot -Z SRR5149059 | ./stream_kmers 6 100 > out.txt` to count k=6 
and with a limit of 100 reads. The specific SRR provided is downloaded but 
never saved and only the counts file is saved. If you already have an `.sra` 
file you can run it on that as well. Streaming gives a speed boost in both 
scenarios.

# Usage
`gsec train --pos-strat bisulfite-seq --pos-org 'homo sapiens' --neg-strat \
wgs --neg-org 'homo sapiens' -k 6 -l 10000 -n 100` downloads and builds a 
classifier to distinguish the positive set from the negative set based on 
k-mer counts of up to k = 6. The limit flag `-l` means that only the first 
10k reads from each fastq are processed, and `-n` specifies the number files.
Keep in mind that some of the attempted downloads fail.
The failed download SRR identification numbers are recorded in the errors.txt 
file, which is generated in your current directory. In addition, a 
`model_summary.txt` is generated in your working directory. The counts files
and models are stored in a specified location in the gsec install locaiton.
The final model is downloaded as a .pkl file which can be loaded back into 
python. 

A unique ID is assigned to each run of `gsec train`, starting with `1`. The
data is saved under the `1/positive` and `1/negative` folders respectively, 
and the model is saved as 1.pkl.


`python gsec-train.py --pos-strat --pos-org --neg-strat --neg-org -k -l -n`
- pos-strat: strategy for positive set
- pos-org: organism for positive set
- neg-strat: strategy for negative set
- neg-org: organism for negative set
- k: maximum size of kmer to count
- l: limit number of reads to use
- n: number of srrs to count for each target (if there are less files that 
match the query, the maximum amount of files matched will be downloaded)

# Project Structure
```bash
.
├── errors.txt
├── gsec
│   ├── gsec_apply.py
│   ├── gsec.py
│   ├── gsec_train.py
│   ├── __init__.py
│   ├── model_building
│   │   ├── create_model.py
│   │   ├── create_model_utils.py
│   │   ├── data
│   │   │   └── 1
│   │   │       ├── negative
│   │   │       │   ├── ERR3523441.txt
│   │   │       │   ├── ERR3523442.txt
│   │   │       │   ├── ERR3523446.txt
│   │   │       │   ├── SRR10000063.txt
│   │   │       │   ├── SRR10000103.txt
│   │   │       │   ├── SRR10000110.txt
│   │   │       │   ├── ...
│   │   │       └── positive
│   │   │           ├── ERR3445822.txt
│   │   │           ├── ERR3674488.txt
│   │   │           ├── ERR3674489.txt
│   │   │           ├── ERR3674493.txt
│   │   │           ├── SRR11348073.txt
│   │   │           ├── ...
│   │   │           ├── SRR11494766.txt
│   │   │           └── SRR8836050.txt
│   │   ├── __init__.py
│   │   ├── ModelRunner.py
│   │   └── __pycache__
│   │       ├── create_model.cpython-37.pyc
│   │       ├── create_model_utils.cpython-37.pyc
│   │       ├── __init__.cpython-37.pyc
│   │       └── ModelRunner.cpython-37.pyc
│   ├── models
│   │   ├── 1.pkl
│   ├── model_test.py  <<<--- is for debugging
│   ├── __pycache__
│   │   ├── gsec_apply.cpython-37.pyc
│   │   ├── gsec.cpython-37.pyc
│   │   ├── gsec_train.cpython-37.pyc
│   │   └── __init__.cpython-37.pyc
│   └── utils
│       ├── countkmers.cpp
│       ├── csv_utils.py
│       ├── __init__.py
│       ├── Makefile
│       ├── __pycache__
│       │   ├── csv_utils.cpython-37.pyc
│       │   └── __init__.cpython-37.pyc
│       ├── stream_kmers
│       └── stream_kmers.cpp
├── gsec.egg-info
│   ├── dependency_links.txt
│   ├── entry_points.txt
│   ├── PKG-INFO
│   ├── requires.txt
│   ├── SOURCES.txt
│   └── top_level.txt
├── MANIFEST.in
├── models.csv
├── model_summary.txt
├── README.md
└── setup.py
```

