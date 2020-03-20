# gsec-train.py: Processes a command from user specifying a search of the
# SRA database, downloads a subset of the data needed, picks a model to
# use, and saves the model for future use.
#
# Authors: Nicolas Perez, Isaac Gelman, Natalie Abreu, Shannon Brownlee,
# Tomas Angelini, Laura Cao, Shreya Havaldar
#
# This software is Copyright (C) 2020 The University of Southern
# California. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and
# its documentation for educational, research and non-profit purposes,
# without fee, and without a written agreement is hereby granted,
# provided that the above copyright notice, this paragraph and the
# following three paragraphs appear in all copies.
#
# Permission to make commercial use of this software may be obtained
# by contacting:
#
# USC Stevens Center for Innovation
# University of Southern California
# 1150 S. Olive Street, Suite 2300
# Los Angeles, CA 90115, USA
#
# This software program and documentation are copyrighted by The
# University of Southern California. The software program and
# documentation are supplied "as is", without any accompanying
# services from USC. USC does not warrant that the operation of the
# program will be uninterrupted or error-free. The end-user
# understands that the program was developed for research purposes and
# is advised not to rely exclusively on the program for any reason.
#
# IN NO EVENT SHALL THE UNIVERSITY OF SOUTHERN CALIFORNIA BE LIABLE TO
# ANY PARTY FOR DIRECT, INDIRECT, SPECIAL, INCIDENTAL, OR
# CONSEQUENTIAL DAMAGES, INCLUDING LOST PROFITS, ARISING OUT OF THE
# USE OF THIS SOFTWARE AND ITS DOCUMENTATION, EVEN IF THE UNIVERSITY
# OF SOUTHERN CALIFORNIA HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH
# DAMAGE. THE UNIVERSITY OF SOUTHERN CALIFORNIA SPECIFICALLY DISCLAIMS
# ANY WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE. THE SOFTWARE PROVIDED

#!/usr/bin/env python

import sys, os, argparse
import subprocess
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import ParseError
from .model_building.create_model_utils import create_dataframe
import pathlib

ROOT = pathlib.Path(__file__).parent.absolute()

def main():
    print('python gsec-train.py pos_strat pos_org neg_strat neg_org \
    max_k limit_reads out_dir num_files')

    parser = argparse.ArgumentParser(description='prepare project config')
    parser.add_argument('--pos-strat', dest='pos_strat', required=True,
                        help='strategy for positive set')
    parser.add_argument('--pos-org', dest='pos_org', required=True,
                        help='organism for positive set')
    parser.add_argument('--neg-strat', dest='neg_strat', required=True,
                        help='strategy for negative set')
    parser.add_argument('--neg-org', dest='neg_org', required=True,
                        help='organism for negative set')
    parser.add_argument('-k', '--k-value', dest='max_k', required=True,
                        type=int, help='maximum size of k-mers')
    parser.add_argument('-l', '--limit-reads', dest='limit_reads',
                        type=int, required=True, help='number of reads to use')
    parser.add_argument('-o', '--outdir', dest='out_dir', required=True,
                        help='output directory')
    parser.add_argument('-n', '--num-files', dest="num_files",
                        type=int, required=True,
                        help='number of files to count from each set')
    args = parser.parse_args()

    # Check if there are temp files from last run
    remove_temp(os.path.join(ROOT,'gsec', 'utils'))

    # Get positive and negative strings
    pos_strat = args.pos_strat
    pos_org = args.pos_org
    neg_strat = args.neg_strat
    neg_org = args.neg_org

    k = args.max_k
    limit = args.limit_reads
    out = args.out_dir
    n = args.num_files

    # Queries
    query(pos_strat, pos_org, n, os.path.join(ROOT, 'gsec','utils', 'pos.xml'))
    query(pos_strat, pos_org, n, os.path.join(ROOT, 'gsec','utils', 'neg.xml'))

    # get srrs
    pos_srrs = parse_xml(os.path.join(ROOT, 'gsec', 'utils', 'pos.xml'), n)
    if len(pos_srrs) == 0:
        print('{}, {} returned no matches...'.format(pos_strat, pos_org))
        return 1


    neg_srrs = parse_xml(os.path.join(ROOT, 'gsec', 'utils', 'neg.xml'), n)
    if len(neg_srrs) == 0:
        print('{}, {} returned no matches...'.format(neg_strat, neg_org))
        return 1

    # delete temp srr files
    remove_temp(os.path.join(ROOT,'gsec', 'utils'))

    # validate directories to save files
    validate_dirs(out)

    # count srrs
    print("<--- Counting positives --->")
    c = 0
    for srr in pos_srrs:
        c+=1
        print("Counting {} [{}/{}]...".format(srr, c, len(pos_srrs)))
        count(k, limit, srr, os.path.join(out,'positive'))

    print("<--- Counting negatives --->")
    c = 0
    for srr in neg_srrs:
        c += 1
        print("Counting {} [{}/{}]...".format(srr, c, len(neg_srrs)))
        count(k, limit, srr, os.path.join(out,'negative'))

    print("Done counting!")

    # create dataframe from count files
    # TODO: alter names of data directories and ask for list of kmers
    df = create_dataframe(
        out, 
        "positive",
        "negative",
        [i for i in range(1, k+1)]
    )
    print(df)
    return 0


def count(k, limit, srr, out):
    """
    k (int): max kmer to count
    limit (int): limit number of reads to count for given file
    srr (str): srr id for read
    out (str): directory to save files
    """
    # check if stream_kmers is compiled
    if ('stream_kmers') not in os.listdir(os.path.join(ROOT, 'gsec', 'utils')):
        # compile
        comp = 'g++ {} -o {}'.format(
            os.path.join(ROOT, 'utils', 'stream_kmers.cpp'),
            os.path.join(ROOT, 'utils', 'stream_kmers')
            )
        print('COMPILING....')
        print(comp)
        subprocess.call(comp, shell=True)

    # shell commands to run
    filename = os.path.join(out, '{}.txt'.format(srr))
    count_path = os.path.join(ROOT, 'gsec','utils', 'stream_kmers')
    fastq = "fastq-dump --skip-technical --split-spot -Z {}".format(srr)
    count = "{} {} {} > {}".format(count_path,
                                     str(k),
                                     str(limit),
                                     str(filename))
    full = fastq + " | " + count
    subprocess.call(full, shell=True)

def query(strat, org, n, temp_path):
    """
    strat (string): strategy to query
    org (string): organism to query
    n (int): number of matches to fetch
    temp_path (string): path to save temp file
    """
    esearch = 'esearch -db sra -query "{}[strategy] AND {}[organism]"'.format(
        strat, org)
    efetch = 'efetch -db sra -format docsum -stop {}'.format(str(n))
    query = esearch + ' | ' + efetch + ' > ' + temp_path

    subprocess.call(query, shell=True)


def parse_xml(filename, n):
    """
    filename (str): name of xml file to read
    n (int): number of srrs to fetch, -1 for all

    returns: (list[str]): list of SRRs to download. Will return empty list if
    query returned no results.
    """
    try:
        tree = ET.parse(filename)
    except ParseError:
        return []

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

def remove_temp(temp_path):
    files = os.listdir(temp_path)
    if "neg.xml" in files:
        os.remove(os.path.join(temp_path,'neg.xml'))
    if "pos.xml" in files:
        os.remove(os.path.join(temp_path,'pos.xml'))

def validate_dirs(out):
    try:
        os.mkdir(out)
    except FileExistsError:
        pass
    try:
        os.mkdir(os.path.join(out, 'positive'))
    except FileExistsError:
        pass
    try:
        os.mkdir(os.path.join(out, 'negative'))
    except FileExistsError:
        pass

if __name__ == '__main__':
    main()
