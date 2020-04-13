# csv-utils.py: utility functions for working with models.csv file
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

import csv
import os
from pathlib import Path


def csv_append(info, file):
    """
    This function takes in an info dictionary and appends it to the csv file
    that contains the reference for ids.
    If the file doesn't exist, it will create it.

    info = {
            id: (int)
            org1: (str),
            strat1: (str),
            org2: (str)
            strat2: (str)
            max_k: (int)
            limit: (int)
    }

    file: name of csv file

    returns: 0 on success, 1 on failure
    """
    fieldnames = ["id", "org1", "strat1", "org2", "strat2", "max_k", "limit"]

    # Check if info is right format
    keys = info.keys()
    if len(keys) != 7:
        return 1
    for field in fieldnames:
        if field not in keys:
            return 1

    # verify if csv exists
    exists = False
    if os.path.isfile(file):
        exists = True

    # append to file
    with open(file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not exists:
            writer.writeheader()

        writer.writerow(info)


def get_next_id(file):
    """
    file: name of csv file
    returns next id to create
    """

    # verify if csv exists and get next id
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            id_ = len(list(reader))
    except IOError:
        id_ = 1

    return id_

'''def __main__():
    next = get_next_id("test_f.csv")
    info = {
            "id": next,
            "org1": "pos_org",
            "strat1": "pos_strat",
            "org2": "neg_org",
            "strat2": "neg_strat",
            "max_k": 6,
            "limit": 10000
    }
    csv_append(info, "test_f.csv")
    print(get_next_id("test_f.csv"))

if __name__ == '__main__':
    __main__()
'''
