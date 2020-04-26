"""
Author: Jake Wachs
Date: 04/20/2020

Machine learning related functions
"""

import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
import numpy as np
import os

from web import scrapeData
from util import readLists

import pandas as pd

def runClustering():
    '''
    Runs k-means clustering algorithm on data
    '''
    positiveURLs = getArticleURLS('optimistc news about coronavirus', 2)
    negativeURLs = getArticleURLS('coronavirus news getting worse', 2)

    positiveArticles = getArticles(positiveURLs)
    negativeArticles = getArticles(negativeURLs)

    articles = positiveArticles + negativeArticles

    for article in articles:
        # run count vectorization on text
        vectorizer = CountVectorizer()
        vectorizer.fit(article.getText())
        vector = vectorizer.transform(article.getText())

    # visualize data
    '''norm = np.linalg.norm(dataset)
    normData = dataset/norm
    x = np.array(normData)
    plt.scatter(x[:,0], x[:,1], label='True Position')
    plt.show()'''


def trainModel():
    '''
    Trains model based on data

    return -- the model itself for prediction purposes
    '''
    fileSize = os.path.getsize('data.txt')

    if fileSize == 0:
        dataset, classification = scrapeData()
    else:
        dataset, classification = readLists()

    gnb = GaussianNB()

    print('TRAINING MODEL...')

    # Split the training and testing data
    x_train, x_test, y_train, y_test = \
        train_test_split(dataset, classification, test_size=0.3)

    model = gnb.fit(x_train, y_train)

    print('MODEL TRAINED.')
    return model, x_test, y_test


def filterArticles(urls, model):
    '''
    Removes negative or indifferent articles from the list

    Keyword Arguments:
    articles -- list of articles from original Google search

    return -- refined list of articles with only positive documents
    '''
    articles = getArticles(urls)

    index = 0
    positiveArticleURLs = []
    for article in articles:
        title = article.getTitle()
        text = article.getText()

        blob0 = TextBlob(title)
        blob1 = TextBlob(text)

        currPair = [blob0.sentiment.polarity, blob1.sentiment.polarity]

        if model.predict([currPair]) == 0:
            positiveArticleURLs.append(urls[index])
        else:
            print('ARTICLE ', article.getTitle(), ' FLAGGED AS NEGATIVE')

        index += 1

    return positiveArticleURLs


def testmodel(model, x_test, y_test):
    '''
    tests model accuracy; for testing purposes only
    '''
    print('testing model...')
    y_predict = model.predict(x_test)

    print('correct classifications:')
    print(y_test)
    print('guesses are:')
    print(y_predict)

    i = 0
    correct = 0
    for prediction in y_predict:
        if prediction == y_test[i]:
            correct = correct + 1
        i = i + 1

    print(correct, '/', len(y_predict), ' or ', correct/len(y_predict), ' correct')