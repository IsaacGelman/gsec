# gsec-apply.py: Run a trained model from local on a new FASTQ file
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
from xml.etree.ElementTree import ParseError
# ROOT = os.path.dirname(os.getcwd())
ROOT = os.path.dirname(os.path.realpath(__file__))


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
    print('python3 gsec.py pos_strat pos_org neg_strat neg_org fastq_file\n')

    """
    pos_strat: (str) strategy for positive set
    pos_org: (str) organism for positive set
    neg_strat: (str) strategy for negative set
    neg_org: (str) organism for negative set
    file: (str) fastq file to be processed
    """

    # TODO will have to change for when there is an actual models.csv file
    # read csv, and split on "," the line
    
    csv_file = csv.reader(open(os.path.join(ROOT, 'model_building/models.csv')), delimiter=",")

    id = -1
    swap_order = False
    # loop through list of models
    for row in csv_file:
        # find matching model
        if pos_org == row[1] and pos_strat == row[2]\
         and neg_org == row[3] and neg_strat == row[4]:
            print("Found Model:", row[1], row[2], "&", row[3], row[4])
            id = row[0]    
            max_k = row[5]
            limit = row[6]
            print("\tModel ID:", id, "... Max k val:", max_k, '\n')
            break
        elif pos_org == row[3] and pos_strat == row[4]\
         and neg_org == row[1] and neg_strat == row[2]:
            swap_order = True
            print("Found Model:", row[3], row[4], ",", row[1], row[2])
            id = row[0]    
            max_k = row[5]
            limit = row[6]
            print("\tModel ID:", id, "... Max k val: ", max_k, '\n')
            break
    if id == -1:
        print("Could not find model matching given strategies.")
        return 1 # no model found
    
    
    
    # open model
    model_dir = os.path.join(ROOT, "models", id+".pkl")
    with open(model_dir, 'rb') as model_pkl:
        model = pickle.load(model_pkl)  

    # count kmers and create dataframe with result
    # TODO  make custom
    cmd = count(max_k, limit, file)
    if not cmd:
        print("ERROR Invalid File")
        return 2 # error

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
    prob = model.predict_proba(df)

    if swap_order:
        result = 1 - result
        prob[0][0], prob[0][1] = prob[0][1], prob[0][0]
    
    # positive is 0, negative is 1
    if not result:
        print("\nPredicted:", pos_strat, pos_org)
        print("\tProbability:", prob[0][0])
    else:
        print("\nPredicted:", neg_strat, neg_org)
        print("\tProbability:", prob[0][1])
    
    
    

    return 0 # success

    
def count(k, limit, fastq):
    """
    k (int): max kmer to count
    limit (int): limit number of reads to count for given file
    fastq (str): fastq file for read
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
    count_path = os.path.join(ROOT, 'utils', 'stream_kmers')

    if not os.path.exists(fastq):
        return
    count = "{} {} {}".format(count_path,
                                     str(k),
                                     str(limit))
    full = "cat " + fastq + " | " + count
    return full

# for testing purposes, remove later
if __name__ == '__main__':
    apply_("bla", "homo sapiens", "blo", "nle", "SRR5149059.fastq")
