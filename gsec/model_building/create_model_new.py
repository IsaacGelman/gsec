# Importing Stuff

import pandas as pd
import numpy as nump
import sklearn as sk
import os
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn import naive_bayes
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegression
from sklearn import neighbors
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import time

# File paths
model_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(model_dir, 'genomics_data')


"""Assumption made on file directories:
 this script is in the same directory as genomics_data folder """

def clear_errors():
    """
    Clear previous errors from file so only new errors from current run
    are recorded
    """
    error_file = open("errors.txt", "w+")
    error_file.write("project_name, file_name, error_type")
    error_file.close()

def dir_check():
    """
    Check directories
    """
    print("model directory: ", model_dir)
    print("data directory: ", data_dir)

def calculate_dimension(kmer_list):
    """
    Function takes list of kmers chosen for the dataset
    and calculates how many rows the corresponding txt files
    should have when processing
    """
    total_count = 0
    for i in kmer_list:
        total_count += pow(4,i)

    return total_count


def file_shell(df,proj,fname, kmer_count, label):
    """
    Append experiment of name "fname" to dataframe
    If number of rows in txt file doesn't match
    appropriate number of kmers, don't append.
    """
    df_new = pd.read_csv(fname, sep='\t', header=None)

    if ((df_new.shape)[0] != kmer_count):
        error_file = open("errors.txt", "a+")
        error_file.write("\r%s, %s, missing_kmers" % (proj.name,
                        fname.name))
        error_file.close()
        return df
    else:
        df_new.set_index(0, inplace=True)
        df_new = df_new.transpose()
        df_new.index = [label]
        return df.append(df_new)


def load_data(data_name, df, kmer_count, label):
    """
    Function loads a certain type of data
    for each experiment, call file_shell
    file_shell returns a dataframe with
    kmer data of most recent experiment
    appended to it
    """

    SRPs = Path(os.path.join(data_dir, data_name))
    for project in SRPs.iterdir():
        if project.is_dir():
            experiment_list = Path(os.path.join(SRPs, project))
            for experiment in experiment_list.iterdir():
                #print("Current exp: %s" % experiment)
                if os.stat(experiment).st_size != 0:
                    df = file_shell(df, project, experiment, kmer_count, label)
                else:
                    #print("ERROR FOUND IN FILE %s" % experiment)
                    error_file = open("errors.txt", "a+")
                    error_file.write("\r%s, %s, empty_file" % (project.name,
                    experiment.name))
    return df

def create_dataframe(first_data_type, second_data_type, kmer_list):
    """
    Function takes inputs the two data types to create the
    dataset from (e.g. wgs vs. rna), and returns a dataframe
    with the kmer counts of both datatypes
    """
    clear_errors()
    df = pd.DataFrame()
    kmer_count = calculate_dimension(kmer_list)
    df = load_data(first_data_type, df, kmer_count, 0)
    df = load_data(second_data_type, df, kmer_count, 1)
    return df

def efficiency_check(first_data_type, second_data_type, kmer_list, n):
    """
    Function runs the dataframe creation process n times and generates
    average runtime stats
    """
    abs_avg = 0
    abs_exp_per_min = 0

    for i in range(0,n):
        tmp_df = pd.DataFrame()
        start_time = time.time()
        tmp_df = create_dataframe(first_data_type, second_data_type, kmer_list)
        end_time = float(time.time() - start_time)
        num_experiments = float(len(tmp_df.index))

        avg = end_time / num_experiments
        exp_per_min = 1 / avg * 60

        abs_avg += avg
        abs_exp_per_min += exp_per_min

    abs_avg = abs_avg / n
    abs_exp_per_min = abs_exp_per_min / n

    print("Average loading time: %f seconds per experiment" % avg)
    print("Experiments to be processed per minute: %f" % exp_per_min)

def main():
    efficiency_check("rna-seq", "wgs_human", [1,2,3,4,5,6], 10)


if __name__ == "__main__":
    main()
