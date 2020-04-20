"""
Author: Jake Wachs
Date: 04/20/2020

Machine learning related functions
"""

from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB
import os

from main import scrapeData

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

    print('dataset is: ', dataset)
    print('classification is: ', classification)

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
        # print('title sentiment: ', blob0.sentiment.polarity)
        # print('text sentiment: ', blob1.sentiment.polarity)

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
