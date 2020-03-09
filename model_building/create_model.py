# Importing Stuff

import pandas as pd
import numpy as np
import sklearn
import os
import pickle
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.linear_model import Lasso



'''
helper function to append new data
'''
def file_shell(df,fname,ind):
    df1 = pd.read_csv(fname, sep='\t', header=None)
    df1.set_index(0, inplace=True)
    df2 = df1.transpose()
    df2.index = [ind]
    df3 = df.append(df2)
    return df3


'''
function: normalize
Normalizes a counts dataframe

Assumes that all values of k from 1 to maxk
are in a counts dataframe, and that all of
the k-mers for any particular value of k are grouped
together

Needs to be modified to take a list of "k" values
in the future after the regularization step is
complete
'''
def normalize(df, maxk):
    start_i = 0
    for k in range(1, maxk+1):
        end_i = start_i + 4**k #end index
        df.iloc[:,start_i:end_i] = df.iloc[:,start_i:end_i].div(df.iloc[:,start_i:end_i].sum(axis=1), axis='rows')
        start_i = end_i
   

'''
function main()

loads data from rna-seq and wgs_human folders
'''
def main():
    df = pd.DataFrame()
    
    basepath_bs = 'data/rna-seq'
    b_entries = Path(basepath_bs)
    for b_entry in b_entries.iterdir():
        if b_entry.is_dir():
            l_entries = Path(b_entry)
            for l_entry in l_entries.iterdir():
                if os.stat(l_entry).st_size != 0:
                    df = file_shell(df,l_entry,0)
    

    basepath_bs = 'data/wgs_human'                   
    b_entries = Path(basepath_bs)
    for b_entry in b_entries.iterdir():
        if b_entry.is_dir():
            l_entries = Path(b_entry)
            for l_entry in l_entries.iterdir():
                if os.stat(l_entry).st_size != 0:
                    df = file_shell(df,l_entry,1)
    
    normalize(df, 6)
    df.dropna(inplace=True)

    y = df.index

    X_train, X_test, y_train, y_test = train_test_split(df.reset_index(drop=True),
                                                        y, 
                                                        test_size=0.25, 
                                                        shuffle=True, 
                                                        stratify=y)
   
    # initialize and train model
    lasso_model = Lasso(alpha = .0005, tol = 1)
    lasso_model.fit(X_train, y_train)
    # cross validation
    pred = 1*(lasso_model.predict(X_test) > 0.5)
    print(classification_report(y_test, pred))
    # print coefficients captured by lasso
    np.set_printoptions(threshold=np.inf)
    coefficients = lasso_model.coef_
    print(df.columns.where(coefficients!=0).dropna())
    # save model
    with open("model.pkl", "wb") as file:
        pickle.dump(lasso_model, file)
        print("saved model as model.pkl")

if __name__ == "__main__":
    main()
