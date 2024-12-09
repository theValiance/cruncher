import os
import pandas as pd
from sklearn import linear_model
from sklearn import svm
from sklearn import neural_network
from sklearn import multioutput
from sklearn import preprocessing
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

dataframe = pd.read_csv('./output.csv')
label_keys = ['energy', 'sharpness', 'mood', 'color']
features = dataframe.drop(labels=label_keys, axis=1).drop(labels=["db_harmonic_min", "db_harmonic_max", "db_percussive_min", "db_percussive_max"], axis=1)
labels = dataframe[label_keys]

scaler = preprocessing.StandardScaler().fit(features)

X_train, X_test, y_train, y_test = train_test_split(scaler.transform(features), labels, test_size=0.3)

#regr = neural_network.MLPRegressor(solver='lbfgs', max_iter=100000)
regr = multioutput.MultiOutputRegressor(svm.SVR(kernel='rbf'))
regr.fit(X_train, y_train)
y_pred = regr.predict(X_test)
print(y_pred)
#print("Coefficients: \n", regr.coef_)
# The coefficients
#print("Coefficients: \n", regr.coef_[0])
print("MSE: {}".format(mean_squared_error(y_test, y_pred, multioutput='raw_values')))
print("R^2: {}".format(r2_score(y_test, y_pred, multioutput='raw_values')))
print("Score: {}".format(regr.score(X_test, y_test)))