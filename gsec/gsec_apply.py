import sys, os, argparse
import subprocess
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
ROOT = os.path.dirname(os.getcwd())


import csv
import pickle
import sklearn
import pandas as pd
from pathlib import Path


def apply_(
    pos_strat,
    pos_org,
    neg_strat,
    neg_org,
    file
):
    print('python3 gsec.py pos_strat pos_org neg_strat neg_org fastq_file')

    """
    pos_strat: (str) strategy for positive set
    pos_org: (str) organism for positive set
    neg_strat: (str) strategy for negative set
    neg_org: (str) organism for negative set
    file: (str) fastq file to be processed
    """

    # TODO will have to change for when there is an actual models.csv file
    # read csv, and split on "," the line
    
    csv_file = csv.reader(open(os.path.join(ROOT, 'gsec/models.csv')), delimiter=",")

    id = -1
    # loop through list of models
    for row in csv_file:
        print(row)
        # find matching model
        if pos_org == row[1] and pos_strat == row[2]\
         and neg_org == row[3] and neg_strat == row[4]:
            print(row)
            id = row[0]    
            max_k = row[5]
            limit = row[6]
            break
        elif pos_org == row[3] and pos_strat == row[4]\
         and neg_org == row[1] and neg_strat == row[2]:
            print(row)
            id = row[0]    
            max_k = row[5]
            limit = row[6]
            break
    if id == -1:
        print("Could not find model matching given strategies.")
        return 1 # no model found
    
    
    
    # open model
    with open("models/" + id + ".pkl", 'rb') as model_pkl:
        model = pickle.load(model_pkl)  

    # count kmers and create dataframe with result
    # TODO  make custom
    cmd = count(max_k, limit, file)
    a = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)

    if sys.version_info[0] < 3: 
        from StringIO import StringIO

    else:
        from io import StringIO

    b = StringIO()
    b.write("kmer\tfreq\n")
    b.write(a.communicate()[0].decode('utf-8'))

    b.seek(0)
    df = pd.read_table(b, usecols={"freq"}, sep="\t")
    df = df.T

    result = model.predict(df)  
    print("\nresult: " + str(result))
    

    return 0 # success

    
def count(k, limit, fastq):
    """
    k (int): max kmer to count
    limit (int): limit number of reads to count for given file
    fastq (str): fastq file for read
    out (str): directory to save files
    """

    # check if stream_kmers is compiled
    if ('stream_kmers') not in os.listdir(os.path.join(ROOT, 'gsec', 'utils')):
        # compile
        comp = 'g++ {} -o {}'.format(
            os.path.join(ROOT, 'gsec', 'utils', 'stream_kmers.cpp'),
            os.path.join(ROOT, 'gsec', 'utils', 'stream_kmers')
            )
        print('COMPILING....')
        print(comp)
        subprocess.call(comp, shell=True)

    # shell commands to run
    count_path = os.path.join(ROOT,  'gsec', 'utils', 'stream_kmers')
    # TODO fastq path should just be what is passed in as argument i think
    # also, will be called from gsec or gsec/gsec ?
    fastq = os.path.join(ROOT, 'gsec', fastq)
    count = "{} {} {}".format(count_path,
                                     str(k),
                                     str(limit))
    full = "cat " + fastq + " | " + count
    return full

# for testing purposes, remove later
if __name__ == '__main__':
    apply_("bla", "homo sapiens", "blo", "nle", "SRR5149059.fastq")