# Importing Stuff

import pandas as pd
import numpy as nump
import sklearn as sk
import os
from pathlib import Path
import pickle as pickle
from sklearn.model_selection import train_test_split
from sklearn import naive_bayes
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score
from sklearn.metrics import accuracy_score
from sklearn.metrics import classification_report
from sklearn.model_selection import GridSearchCV
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LinearRegression
from sklearn.linear_model import LogisticRegressionCV
from sklearn import neighbors
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import Lasso
from sklearn import linear_model
import time
from glob import glob

# file paths and names
model_dir = os.path.dirname(os.path.realpath(__file__))
data_dir = os.path.join(model_dir, 'genomics_data')

existing_models = glob(model_dir + '*.pkl')
model_filename = model_dir + 'model%d.pkl' % (len(existing_models) + 1)


# function to normalize data
def normalize(df, maxk):
  start_index = 0
  for k in range(1,maxk+1):
    df.iloc[:,start_index:start_index+4**k] = \
    df.iloc[:,start_index:start_index+4**k].div(
        df.iloc[:,start_index:start_index+4**k].sum(axis=1), axis='rows')

    start_index = start_index+4**k

# function for creating and saving model
def create_model(df, maxk):

    # normalize
    normalize(df,maxk)
    df.dropna(inplace=True)

    # split train and test
    y = df.index
    X_train, X_test, y_train, y_test = train_test_split(
        df.reset_index(drop=True), y, test_size=0.25, shuffle=True,
                       stratify=y)

    # init dictionaries
    model_scores = {}
    model_types = {}

    # models

    # log-reg
    log_reg = LogisticRegressionCV(cv=5, random_state=0)
    print(cross_val_score(log_reg, X_train, y_train, cv=3))
    log_reg.fit(X_train, y_train)

    pred = log_reg.predict(X_test)
    scores = log_reg.predict_proba(X_test)[:, 1]

    print('Accuracy: ', accuracy_score(y_test, pred))
    print('AUROC: ', roc_auc_score(y_test, scores))
    print(classification_report(y_test, pred))

    model_scores['logistic'] = accuracy_score(y_test, pred)
    model_types['logistic'] = log_reg

    # knn
    base_knn = neighbors.KNeighborsClassifier()
    parameters = {
        'n_neighbors': [1, 2, 5, 10, 15, 25],
        'weights': ['uniform', 'distance']
        }

    knn = GridSearchCV(base_knn, parameters, cv=3)
    print(cross_val_score(knn, X_train, y_train, cv=3))
    knn.fit(X_train, y_train)
    print('Best Hyperparameters: ', knn.best_params_, '\n')

    pred = knn.predict(X_test)
    scores = knn.predict_proba(X_test)[:, 1]

    print('Accuracy: ', accuracy_score(y_test, pred))
    print('AUROC: ', roc_auc_score(y_test, scores))
    print(classification_report(y_test, pred))

    model_scores['knn'] = accuracy_score(y_test, pred)
    model_types['knn'] = knn

    # gauss nb
    base_gnb = GaussianNB()
    parameters = {'var_smoothing': [1e-20, 1e-15, 1e-10, 1e-05, 1e01, 1e-05]}

    gnb = GridSearchCV(base_gnb, parameters, cv=3)
    print(cross_val_score(gnb, X_train, y_train, cv=3))
    gnb.fit(X_train, y_train)
    print('Best Hyperparameters: ', gnb.best_params_, '\n')

    pred = gnb.predict(X_test)
    scores = gnb.predict_proba(X_test)[:, 1]

    print('Accuracy: ', accuracy_score(y_test, pred))
    print('AUROC: ', roc_auc_score(y_test, scores))
    print(classification_report(y_test, pred))

    model_scores['gaussnb'] = accuracy_score(y_test, pred)
    model_types['gaussnb'] = gnb

    # random forest
    base_rf = RandomForestClassifier(n_estimators=50)
    parameters = {
        'bootstrap': [True],
         'max_depth': [90, 100],
          'n_estimators': [50, 100, 200]
    }

    rf = GridSearchCV(base_rf, parameters, cv=3)
    print(cross_val_score(rf, X_train, y_train, cv=3))
    rf.fit(X_train, y_train)

    pred = rf.predict(X_test)
    scores = rf.predict_proba(X_test)[:, 1]

    print('Accuracy: ', accuracy_score(y_test, pred))
    print('AUROC: ', roc_auc_score(y_test, scores))
    print(classification_report(y_test, pred))

    model_scores['forest'] = accuracy_score(y_test, pred)
    model_types['forest'] = rf

    # ensemble
    eclf = VotingClassifier(estimators=[
        ('gnb', gnb),
        ('lr', log_reg),
        ('rf', rf)],
        voting='soft')

    print(cross_val_score(eclf, X_train, y_train, cv=3))
    eclf.fit(X_train, y_train)

    pred = eclf.predict(X_test)
    scores = eclf.predict_proba(X_test)[:, 1]

    print('Accuracy: ', accuracy_score(y_test, pred))
    print('AUROC: ', roc_auc_score(y_test, scores))
    print(classification_report(y_test, pred))

    model_scores['ensemble'] = accuracy_score(y_test, pred)
    model_types['ensemble'] = eclf

    # lasso
    lasso = Lasso()
    parameters = {'alpha': [1e-15, 1e-10, 1e-8, 1e-4, 1e-3, 1e-2, 1, 5, 10]}
    lassoclf = linear_model.Lasso(alpha=.0005, tol=1)
    print(cross_val_score(lassoclf, X_train, y_train, cv=3))
    lassoclf.fit(X_train, y_train)

    nump.set_printoptions(threshold=nump.inf)
    coefficients = lassoclf.coef_
    df.columns.where(coefficients != 0).dropna()

    pred = lassoclf.predict(X_test)

    print('Accuracy: ', accuracy_score(y_test, 1 * (pred > 0.5)))
    print(classification_report(y_test, 1 * (pred > 0.5)))

    model_scores['log-reg'] = accuracy_score(y_test, 1 * (pred > 0.5))
    model_types['log-reg'] = lassoclf

    # get best model
    max_score = -1.0
    for key in model_scores:
        if model_scores[key] > max_score:
            max_score = model_scores[key]
            model_type_string = key

    # save model
    with open(model_filename, "wb") as file:
        pickle.dump(model_types[model_type_string], file)

    return df