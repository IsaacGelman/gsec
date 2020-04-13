# ModelRunner.py: trains and save best model. Also writes to summary file.
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

import numpy as np
import pandas as pd
import os
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split, GridSearchCV, \
cross_val_score
from sklearn import naive_bayes
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import roc_auc_score, accuracy_score, \
classification_report, confusion_matrix
from sklearn.ensemble import RandomForestClassifier, VotingClassifier
from sklearn.linear_model import LinearRegression, LogisticRegressionCV, Lasso
from sklearn.linear_model import LogisticRegression
from sklearn import neighbors
from sklearn.preprocessing import StandardScaler

class ModelRunner():

    def __init__(self, df):
        # create splits
        y = df.index
        self.X_train, \
        self.X_test, \
        self.y_train, \
        self.y_test = train_test_split(
            df.reset_index(drop=True),
            y,
            test_size=0.25)
            # shuffle=True,
            # stratify=y)
        print("y:\n",y)
        print("ytrain:\n",self.y_train)

        # scaler
        # model_scaler = preprocessing.StandardScaler().fit(self.X_train)
        # X_train_scaled = model_scaler.transform(self.X_train)
        # X_test_scaled = model_scaler.transform(self.X_test)
        # self.X_train = pd.DataFrame(X_train_scaled, index=self.X_train.index,
        #     columns=self.X_train.columns)
        # self.X_test = pd.DataFrame(X_test_scaled, index=self.X_test.index,
        #     columns=self.X_test.columns)

        # models
        self.models = {}

        # create new summary file
        with open("model_summary.txt", "w") as ms:
            pass

    def log_reg(self):
        log_reg = LogisticRegression()
        log_reg.fit(self.X_train, self.y_train)

        pred_train = log_reg.predict(self.X_train)

        with open("model_summary.txt", "a") as summary:
            summary.write("SUMMARY {}: \n".format("Logistic Regression TRAIN"))
            summary.write("Confusion Matrix: \n")
            summary.write(str(confusion_matrix(self.y_train, pred_train)))
            summary.write("\n")
            summary.write("Classification Report: \n")
            summary.write(classification_report(self.y_train, pred_train))
            summary.write("\n =================================== \n")

        pred = log_reg.predict(self.X_test)

        # Record summary and save
        self.write_summary("Logistic Regression TEST", pred)
        self.models['log_reg'] = (log_reg, accuracy_score(self.y_test, pred))

    # def log_reg(self):
    #     log_reg = LogisticRegressionCV(cv=5, random_state=0, solver="liblinear")
    #     log_reg.fit(self.X_train, self.y_train)

    #     pred = log_reg.predict(self.X_test)

    #     # Record summary and save
    #     self.write_summary("Logistic Regression CV", pred)
    #     self.models['log_reg'] = (log_reg, accuracy_score(self.y_test, pred))

    def knn(self):
        base_knn = neighbors.KNeighborsClassifier()
        parameters = {
            'n_neighbors': [1, 2, 5, 10, 15, 25],
            'weights': ['uniform', 'distance']
        }

        knn = GridSearchCV(base_knn, parameters, cv=3)
        knn.fit(self.X_train, self.y_train)

        pred_train = knn.predict(self.X_train)

        with open("model_summary.txt", "a") as summary:
            summary.write("SUMMARY {}: \n".format("KNN TRAIN"))
            summary.write("Confusion Matrix: \n")
            summary.write(str(confusion_matrix(self.y_train, pred_train)))
            summary.write("\n")
            summary.write("Classification Report: \n")
            summary.write(classification_report(self.y_train, pred_train))
            summary.write("\n =================================== \n")


        pred = knn.predict(self.X_test)

        # Record summary and save
        self.write_summary("KNN", pred)
        self.models['knn'] = (knn, accuracy_score(self.y_test, pred))

    def gnb(self):
        base_gnb = GaussianNB()
        parameters = {'var_smoothing': [1e-20, 
                                        1e-15, 
                                        1e-10, 
                                        1e-05, 
                                        1e01, 
                                        1e-05]}    
        gnb = GridSearchCV(base_gnb, parameters, cv=3)
        gnb.fit(self.X_train, self.y_train)
        
        # delete me
        pred_train = gnb.predict(self.X_train)
        with open("model_summary.txt", "a") as summary:
            summary.write("SUMMARY {}: \n".format("gaussian nb TRAIN"))
            summary.write("Confusion Matrix: \n")
            summary.write(str(confusion_matrix(self.y_train, pred_train)))
            summary.write("\n")
            summary.write("Classification Report: \n")
            summary.write(classification_report(self.y_train, pred_train))
            summary.write("\n =================================== \n")

        pred = gnb.predict(self.X_test)

        # Record summary and save
        self.write_summary("Gaussian Naive Bayes", pred)
        self.models['gaussnb'] = (gnb, accuracy_score(self.y_test, pred))

    def rf(self):
        # random forest
        base_rf = RandomForestClassifier(n_estimators=50)
        parameters = {
            'bootstrap': [True],
             'max_depth': [90, 100],
              'n_estimators': [50, 100, 200]
        }
        rf = GridSearchCV(base_rf, parameters, cv=3)
        rf.fit(self.X_train, self.y_train)
        pred = rf.predict(self.X_test)

        # Record summary and save
        self.write_summary("Random Forests", pred)
        self.models['rand_forest'] = (rf, accuracy_score(self.y_test, pred))

    def ensemble(self):
        # get model name and trained model
        estimators = [(item[0], item[1][0]) for item in self.models.items()]
        eclf = VotingClassifier(estimators=estimators,voting='soft')

        eclf.fit(self.X_train, self.y_train)

        pred = eclf.predict(self.X_test)

        # Record summary and save
        self.write_summary("Ensemble", pred)
        self.models['ensemble'] = (eclf, accuracy_score(self.y_test, pred))

    def lasso(self):
        # lasso
        parameters = {'alpha': [1e-15, 1e-10, 1e-8, 1e-4, 1e-3, 1e-2, 1, 5, 10]}
        lassoclf = Lasso(alpha=.0005, tol=1)
        lassoclf.fit(self.X_train, self.y_train)

        pred = lassoclf.predict(self.X_test)

        # Record summary and save
        # self.write_summary("Lasso Regression", pred)
        self.models['lasso'] = (lassoclf, accuracy_score(self.y_test, pred))



    def get_best_model(self):
        """
        returns the best model and max score (in this order) 
        """
        max_score = -1.0
        best_model = None

        for model in self.models.values():
            if model[1] > max_score:
                max_score = model[1]
                best_model = model[0]

        return best_model, max_score
    
    def save_model(self, model, file_dir):
        """
        model: model to save
        file_dir: path to save model file
        """
        with open(file_dir, "wb") as file:
            pickle.dump(model, file)

    def write_summary(self, model_name, pred):
        """
        model_name: str
        pred: vector with predicted values
        """

        with open("model_summary.txt", "a") as summary:
            summary.write("SUMMARY {}: \n".format(model_name))
            summary.write("Confusion Matrix: \n")
            summary.write(str(confusion_matrix(self.y_test, pred)))
            summary.write("\n")
            summary.write("Classification Report: \n")
            summary.write(classification_report(self.y_test, pred))
            summary.write("\n =================================== \n")
