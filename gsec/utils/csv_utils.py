import csv
import os


def append(info, file):
    """
    This function takes in an info dictionary and appends it to the csv file
    that contains the reference for ids.
    If the file doesn't exist, it will create it.

    info = {
            org1: (str),
            strat1: (str),
            org2: (str)
            strat2: (str)
    } 

    csv: path of csv file 

    returns: 0 on success, 1 on failure
    """
    # Check if info is right format
    keys = info.keys()
    if len(keys) != 4:
        return 1
    for field in ["org1", "strat1", "org2", "strat2"]:
        if field not in keys:
            return 1

    # verify if csv exists and get next id
    exists = False
    try:
        with open(file, 'r') as f:
            reader = csv.reader(f, delimiter=",")
            id_ = len(list(reader))
            exists = True
    except IOError:
        id_ = 1

    # append to file
    fieldnames = ["id", "org1", "strat1", "org2", "strat2"]
    info["id"] = id_

    with open(file, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

        if not exists:
            writer.writeheader()

        writer.writerow(info)


def get(info):
    """
    info = {
            org1: (str),
            strat1: (str),
            org2: (str)
            strat2: (str)
    }

    returns: id
    """
    pass
