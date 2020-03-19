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


def main():
    print('python3 gsec.py pos_strat pos_org neg_strat neg_org fastq_file')

    parser = argparse.ArgumentParser(description='prepare project config')
    parser.add_argument('--pos-strat', dest='pos_strat', required=True,
                        help='strategy for positive set')
    parser.add_argument('--pos-org', dest='pos_org', required=True,
                        help='organism for positive set')
    parser.add_argument('--neg-strat', dest='neg_strat', required=True,
                        help='strategy for negative set')
    parser.add_argument('--neg-org', dest='neg_org', required=True,
                        help='organism for negative set')
    parser.add_argument('-f', '--file', dest='fastq_file', required=True,
                        help='fastq file')
    args = parser.parse_args()


    # Get positive and negative strings
    pos_strat = args.pos_strat
    pos_org = args.pos_org
    neg_strat = args.neg_strat
    neg_org = args.neg_org

    # Get fastq file
    file = args.fastq_file

    # TODO will have to change for when there is an actual models.csv file
    # read csv, and split on "," the line
    
    csv_file = csv.reader(open(os.path.join(ROOT, 'utils/models.csv')), delimiter=",")
    # csv_file = csv.reader(open('models.csv', "rb"), delimiter=",")


    # loop through list of models
    for row in csv_file:
        print(row)
        # if current rows first and second col match pos & neg strats, use that model
        if pos_strat == row[0] and neg_strat == row[1]:
            print(row)
            model_pkl = row[2]
            k_vals = row[3]
            classifier = row[4]
    
    print(model_pkl, k_vals, classifier)

    with open(model_pkl, 'rb') as model_pkl:
        model = pickle.load(model_pkl)   

    print(model)
    print(file)

    out = os.path.join(ROOT, 'gsec')
    print(out)
    # subprocess.call("cat " + count(3, 1000, file, out), shell=True)

    df = pd.DataFrame()
    
    basepath_bs = count(6, 1000, file, out)
    entry = Path(basepath_bs)
    print(entry)
    if os.stat(entry).st_size != 0:
        df = file_shell(df,entry,0)
    df.dropna(inplace=True)

    print(df)

    result = model.predict(df)  
    print(result)
    

    return

    


def count(k, limit, fastq, out):
    """
    k (int): max kmer to count
    limit (int): limit number of reads to count for given file
    fastq (str): fastq file for read
    out (str): directory to save files
    """

    print(ROOT)

    # check if stream_kmers is compiled
    if ('stream_kmers') not in os.listdir(os.path.join(ROOT, 'utils')):
        # compile
        comp = 'g++ {} -o {}'.format(
            os.path.join(ROOT, 'utils', 'stream_kmers.cpp'),
            os.path.join(ROOT, 'utils', 'stream_kmers')
            )
        print('COMPILING....')
        print(comp)
        subprocess.call(comp, shell=True)

    # shell commands to run
    filename = os.path.join("../temp", '{}.txt'.format(fastq[:-6]))
    count_path = os.path.join("..", 'utils', 'stream_kmers')
    fastq = os.path.join("..", 'utils', fastq)
    count = "{} {} {} > {}".format(count_path,
                                     str(k),
                                     str(limit),
                                     str(filename))
    full = "cat " + fastq + " | " + count
    subprocess.call(full, shell=True)
    return filename

def file_shell(df,fname,ind):
    """
    helper function to append new data
    """
    df1 = pd.read_csv(fname, sep='\t', header=None)
    df1.set_index(0, inplace=True)
    df2 = df1.transpose()
    df2.index = [ind]
    df3 = df.append(df2)
    return df3

if __name__ == '__main__':
    main()


