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

#!/usr/bin/env python3

import sys, os, argparse
import subprocess
import xml.etree.ElementTree as ET
from pathlib import Path
from xml.etree.ElementTree import ParseError
from .model_building.create_model_utils import create_dataframe
from .model_building.create_model import create_model
from .utils.csv_utils import csv_append, get_next_id

ROOT = os.path.dirname(os.path.realpath(__file__))

def main(
    pos_strat,
    pos_org,
    neg_strat,
    neg_org,
    k,
    limit,
    n
):
    """
    pos_strat: (str) strategy for positive set
    pos_org: (str) organism for positive set
    neg_strat: (str) strategy for negative set
    neg_org: (str) organism for negative set
    k (int): max kmer to count
    limit (int): limit of reads for each run
    n (int): number of files for each set
    """

    # Check if there are temp files from last run
    remove_temp(os.path.join(ROOT, 'utils'))

    # Queries
    query(pos_strat, pos_org, n, os.path.join(ROOT,'utils', 'pos.xml'))
    query(pos_strat, pos_org, n, os.path.join(ROOT,'utils', 'neg.xml'))

    # get srrs
    pos_srrs = parse_xml(os.path.join(ROOT, 'utils', 'pos.xml'), n)
    if len(pos_srrs) == 0:
        print('{}, {} returned no matches...'.format(pos_strat, pos_org))
        return 1


    neg_srrs = parse_xml(os.path.join(ROOT, 'utils', 'neg.xml'), n)
    if len(neg_srrs) == 0:
        print('{}, {} returned no matches...'.format(neg_strat, neg_org))
        return 1

    # delete temp srr files
    remove_temp(os.path.join(ROOT, 'utils'))

    # validate directories to save files
    id_dir = validate_dirs(get_next_id())

    # count srrs
    print("<--- Counting positives --->")
    c = 0
    for srr in pos_srrs:
        c+=1
        print("Counting {} [{}/{}]...".format(srr, c, len(pos_srrs)))
        count(k, limit, srr, os.path.join(id_dir,'positive'))

    print("<--- Counting negatives --->")
    c = 0
    for srr in neg_srrs:
        c += 1
        print("Counting {} [{}/{}]...".format(srr, c, len(neg_srrs)))
        count(k, limit, srr, os.path.join(id_dir,'negative'))

    print("Done counting!")

    # add id to csv
    info = {
            "id": get_next_id(out),
            "org1": pos_org,
            "strat1": pos_strat,
            "org2": neg_org,
            "strat2": neg_strat,
    }
    csv_append(info, out)


    # create dataframe from count files
    # TODO: alter names of data directories and ask for list of kmers
    df = create_dataframe(
        id_dir,
        "positive",
        "negative",
        [i for i in range(1, k+1)]
    )

    # check if dataframe is empty: if it is, not enough data and must abort
    if(df.empty):
        return 1
    # if not, use returned dataframe to train models and return
    else:
        if(create_model(df, k) != 0):
            print("Model building failed. Aborting")

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
    filename = os.path.join(out, '{}.txt'.format(srr))
    count_path = os.path.join(ROOT, 'utils', 'stream_kmers')
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

def validate_dirs(id):
    """
    This function will create relevant directories to save count files.
    id: id of the set of data to use as name of directory

    returns: directory to save new id
    """
    # setting up paths
    data = os.path.join(ROOT, "model_building", "data")
    id_dir = os.path.join(data, str(id))
    positive = os.path.join(id_dir, "positive")
    negative = os.path.join(id_dir, "negative")

    # Create directories
    for directory in [data, id_dir, positive, negative]:
        if not os.path.exists(directory):
            os.mkdir(directory)

    return id_dir
    

if __name__ == '__main__':
    main()
