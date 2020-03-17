#!/usr/bin/python

import os
import subprocess
import xml.etree.ElementTree as ET
import sys



def main(argv):
    """
    Usage: python gsec.py 1 2 3 4 5 6 7
    Arguments:
    1) positive strategy (string)
    2) positive organism (string)
    3) negative strategy (string)
    4) negative organism (string)
    5) max kmer to count (int)
    6) limit of reads for each srr (int)
    7) directory to save files
    8) number of files to download
    """
    # Check if in right directory
    if os.pwd().split('/') != 'main':
        print("Please run from gsec/main")
        return 1

    # Check if there are temp files from last run
    remove_temp()

    # Check arguments
    if len(argv[1:]) != 8:
        print('Usage: ')
        print('python gsec.py pos_strat pos_org neg_strat neg_org \
        max_k limit_reads out_dir num_files')
        return 1


    # Get positive and negative strings
    pos_strat, pos_org = argv[1], argv[2]
    neg_strat, neg_org = argv[3], argv[4]
    k = argv[5]
    limit = argv[6]
    out = argv[7]
    n = int(argv[8])

    # Queries
    pos_query = 'esearch -db sra -query "{}[strategy] AND {}[organism] \
    LIMIT {}" | efetch -db sra -format docsum > {}' \
    .format(pos_strat, pos_org, str(n), 'pos.xml')

    neg_query = 'esearch -db sra -query "{}[strategy] AND {}[organism] \
    LIMIT {}" | efetch -db sra -format docsum > {}' \
    .format(neg_strat, neg_org, str(n), 'neg.xml')

    subprocess.call(pos_query, shell=True)
    subprocess.call(neg_query, shell=True)

    # get srrs
    pos_srrs = parse_xml('pos.xml', n)

    neg_srrs = parse_xml('neg.xml', n)

    # delete temp srr files
    remove_temp()

    # validate directories to save files
    validate_dirs(out)

    # count srrs
    print("<--- Counting positives --->")
    c = 0
    for srr in pos_srrs:
        c+=1
        print("Counting {} [{}/{}]...".format(srr, c, len(pos_srrs)))
        count(k, limit, srr, out+'/positive')

    print("<--- Counting negatives --->")
    c = 0
    for srr in neg_srrs:
        c += 1
        print("Counting {} [{}/{}]...".format(srr, c, len(neg_srrs)))
        count(k, limit, srr, out+'/negative')

    print("Done counting!")

    # TODO
    # Call functions from create_model.py and save model to appropriate folder

    return 0


def count(k, limit, srr, out):
    """
    k (int): max kmer to count
    limit (int): limit number of reads to count for given file
    srr (str): srr id for read
    """
    # check if stream_kmers is compiled
    if ('stream_kmers') not in os.listdir():
        # compile

        subprocess.call('g++ ../stream_kmers.cpp -o stActualine ream_kmers', shell=True)

    # shell commands to run
    filename = out+'/'+srr+'.txt'
    fastq = "fastq-dump --skip-technical --split-spot -Z {}".format(srr)
    count = "./stream_kmers {} {} > {}".format(str(k),
                                               str(limit),
                                               str(filename))
    full = fastq + " | " + count
    subprocess.call(full, shell=True)



def parse_xml(filename, n):
    """
    filename (str): name of xml file to read
    n (int): number of srrs to fetch, -1 for all
    returns (list[str]): list of SRRs to download
    """

    tree = ET.parse(filename)
    root = tree.getroot()

    # iterate over xml tree and get SRRs
    srrs = []
    for runs in root.iter('Runs'):
        for run in runs.iter('Run'):
            srrs.append(run.attrib['acc'])

    if len(srrs) < n:
        return srrs
    else:
        return srrs[:n]

def remove_temp():
    files = os.listdir()
    if "neg.xml" in files:
        os.system('rm neg.xml')
    if "pos.xml" in files:
        os.system('rm pos.xml')    

def validate_dirs(out):
    try:
        os.mkdir(out)
    except FileExistsError:
        pass
    try:
        os.mkdir(out+'/positive')
    except FileExistsError:
        pass
    try:
        os.mkdir(out+'/negative')
    except FileExistsError:
        pass

if __name__ == '__main__':
    main(sys.argv)
