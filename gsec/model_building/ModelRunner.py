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
from sklearn import neighbors
from sklearn import preprocessing

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
            test_size=0.25,
            shuffle=True,
            stratify=y
            )

        # scaler
        model_scaler = preprocessing.StandardScaler().fit(self.X_train)
        X_train_scaled = model_scaler.transform(self.X_train)
        X_test_scaled = model_scaler.transform(self.X_test)
        self.X_train = pd.DataFrame(X_train_scaled, index=self.X_train.index, columns=self.X_train.columns)
        self.X_test = pd.DataFrame(X_test_scaled, index=self.X_test.index, columns=self.X_test.columns)

        # models
        self.models = {}

    def log_reg(self, print_matrix=False):
        log_reg = LogisticRegressionCV(cv=5, random_state=0)
        log_reg.fit(self.X_train, self.y_train)

        pred = log_reg.predict(self.X_test)
        if print_matrix:
            print("Confusion Matrix: ")
            print(confusion_matrix(self.y_train, pred))

        self.models['log_reg'] = (log_reg, accuracy_score(self.y_test, pred))

    def knn(self, print_matrix=False):
        base_knn = neighbors.KNeighborsClassifier()
        parameters = {
            'n_neighbors': [1, 2, 5, 10, 15, 25],
            'weights': ['uniform', 'distance']
        }

        knn = GridSearchCV(base_knn, parameters, cv=3)
        knn.fit(self.X_train, self.y_train)

        pred = knn.predict(self.X_test)

        if print_matrix:
            print("Confusion Matrix: ")
            print(confusion_matrix(self.y_train, pred))

        self.models['knn'] = (knn, accuracy_score(self.y_test, pred))

    def gnb(self, print_matrix=False):
        base_gnb = GaussianNB()
        parameters = {'var_smoothing': [1e-20, 
                                        1e-15, 
                                        1e-10, 
                                        1e-05, 
                                        1e01, 
                                        1e-05]}    
        gnb = GridSearchCV(base_gnb, parameters, cv=3)
        gnb.fit(self.X_train, self.y_train)
        pred = gnb.predict(self.X_test)

        if print_matrix:
            print("Confusion Matrix: ")
            print(confusion_matrix(self.y_train, pred))
        self.models['gaussnb'] = (gnb, accuracy_score(self.y_test, pred))

    def rf(self, print_matrix=False):
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

        if print_matrix:
            print("Confusion Matrix: ")
            print(confusion_matrix(self.y_train, pred))
        self.models['rand_forest'] = (rf, accuracy_score(self.y_test, pred))

    def ensemble(self, print_matrix=False):
        # get model name and trained model
        estimators = [(item[0], item[1][0]) for item in self.models.items()]
        eclf = VotingClassifier(estimators=estimators,voting='soft')

        eclf.fit(self.X_train, self.y_train)

        pred = eclf.predict(self.X_test)

        if print_matrix:
            print("Confusion Matrix: ")
            print(confusion_matrix(self.y_train, pred))

        self.models['ensemble'] = (eclf, accuracy_score(self.y_test, pred))

    def lasso(self, print_matrix=False):
        # lasso
        parameters = {'alpha': [1e-15, 1e-10, 1e-8, 1e-4, 1e-3, 1e-2, 1, 5, 10]}
        lassoclf = Lasso(alpha=.0005, tol=1)
        print(cross_val_score(lassoclf, self.X_train, self.y_train, cv=3))
        lassoclf.fit(self.X_train, self.y_train)

        np.set_printoptions(threshold=np.inf)
        coefficients = lassoclf.coef_
        df.columns.where(coefficients != 0).dropna()

        pred = lassoclf.predict(self.X_test)

        if print_matrix:
            print("Confusion Matrix: ")
            print(confusion_matrix(self.y_train, pred))

        # print('Accuracy: ', accuracy_score(y_test, 1 * (pred > 0.5)))
        # print(classification_report(y_test, 1 * (pred > 0.5)))

        # model_scores['log-reg'] = accuracy_score(y_test, 1 * (pred > 0.5))
        # model_types['log-reg'] = lassoclf


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