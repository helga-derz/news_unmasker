# -*- coding: utf-8 -*-

import making_vectors as mv
from sklearn.svm import SVC
import numpy as np

'''
print "reading data"
### reading data
#TRAIN
x_train = []
y_train = []
for numb in range(10, 17):

    relations = mv.get_relations('event' + str(numb))

    docs = mv.read_docs('event' + str(numb))

    for key in relations.keys():

        text1index = int(key.split('.')[0].split('_')[1])
        text2index = int(key.split('.')[1].split('_')[1])

        x_train.append(mv.compare(docs[text1index], docs[text2index]))
        y_train.append(relations[key])



#TEST
x_test = []
y_test = []

for numb in range(10):

    relations = mv.get_relations('event' + str(numb))

    docs = mv.read_docs('event' + str(numb))

    for key in relations.keys():

        text1index = int(key.split('.')[0].split('_')[1])
        text2index = int(key.split('.')[1].split('_')[1])

        x_test.append(mv.compare(docs[text1index], docs[text2index]))
        y_test.append(relations[key])
'''


def classificate(x_train, y_train, x_test):   # на вход ВЕКТОРЫ и список категорий

    # creating model
    model = SVC(kernel='precomputed')

    # loading kernel + fiting model
    print "train kernel"

    kernel_train = []
    for vector in x_train:
        t = []
        for vector1 in x_train:
            t.append(np.dot(vector, vector1))
        kernel_train.append(t)

    model.fit(kernel_train, y_train)

    # loading train set + predicting labels #
    print "test kernel"

    kernel_test = []
    for vector in x_test:
        t = []
        for vector1 in x_train:
            t.append(np.dot(vector, vector1))
        kernel_test.append(t)

    return model.predict(kernel_test)


def kernel_train(x_train):
    # loading kernel + fiting model
    print "train kernel"

    kernel_train = []
    for vector in x_train:
        t = []
        for vector1 in x_train:
            t.append(np.dot(vector, vector1))
        kernel_train.append(t)

    return kernel_train


def kernel_test(x_train, x_test):
    print "test kernel"

    kernel_test = []
    for vector in x_test:
        t = []
        for vector1 in x_train:
            t.append(np.dot(vector, vector1))
        kernel_test.append(t)

    return kernel_test

'''
n = 0
for i in range(len(y_predicted)):
    if y_test[i] == y_predicted[i]:
        n += 1

print n, len(y_test)'''
