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
    '''
    clear previous errors from file so only new errors from current run
    are recorded
    '''
    error_file = open("errors.txt", "w+")
    error_file.write("project_name, file_name, error_type")

def dir_check():
    """
    Check directories
    """
    print("model directory: ", model_dir)
    print("data directory: ", data_dir)


def file_shell(df,proj,fname,ind):
    """
    Append experiment of name "fname" to dataframe
    """
    df_new = pd.read_csv(fname, sep='\t', header=None)

    '''
    If number of rows in txt file doesn't match number of kmers, don't append
    '''
    if not df.empty:
        if ((df_new.shape)[0] != (df.shape)[1]):
            error_file = open("errors.txt", "a+")
            error_file.write("\r%s, %s, missing_kmers" % (proj.name,
            fname.name))
            return df

    df_new.set_index(0, inplace=True)
    df_new = df_new.transpose()
    df_new.index = [ind]
    return df.append(df_new)


def load_data(data_name, df):
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
                    df = file_shell(df, project, experiment, 1)
                else:
                    #print("ERROR FOUND IN FILE %s" % experiment)
                    error_file = open("errors.txt", "a+")
                    error_file.write("\r%s, %s, empty_file" % (project.name,
                    experiment.name))
    return df


def main():
    clear_errors()
    start_time = time.time()
    df = pd.DataFrame()
    # dir_check()
    #df = load_data("rna-seq", df)
    df = load_data("wgs_human", df)

    end_time = float(time.time() - start_time)
    num_experiments = float(len(df.index))
    avg = end_time / num_experiments
    exp_per_min = 1 / avg * 60


    print("Average loading time: %f seconds per experiment" % avg)
    print("Experiments to be processed per minute: %f" % exp_per_min)
    print(df.shape)


if __name__ == "__main__":
    main()
