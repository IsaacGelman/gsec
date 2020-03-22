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
