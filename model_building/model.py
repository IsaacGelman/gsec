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

data = /home/data

# Load Files into Data Frame
def file_shell(df,fname,ind):
      df1 = pd.read_csv(fname, sep='\t', header=None)
        df1.set_index(0, inplace=True)
          df2 = df1.transpose()
            df2.index = [ind]
              df3 = df.append(df2)
                return df3


