"""
Author: Jake Wachs
Date: 04/02/2020

Beacon - A shining light in the storm
"""

from classes.Article import Article

import newspaper
import time
from pprint import pprint       # FIXME: just for testing purposes
import requests
from textblob import TextBlob   # for sentiment analysis
from selenium import webdriver  # FIXME: does Google have an API I can use instead of Selenium
from selenium.webdriver.common.keys import Keys

from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB

def getArticleURLS(query):
    '''
    Gets list of good news article URLs about COVID-19

    Automatically Googles good news articles about COVID-19 and returns
    a list of those articles' URLs

    return -- list of URLs of articles
    '''
    driver = webdriver.Firefox()
    driver.get('https://www.google.com')

    que = driver.find_element_by_xpath("//input[@name='q']")
    que.send_keys(query)
    que.send_keys(Keys.RETURN)

    # Wait for browser to get to new page before finding links
    time.sleep(2)

    links = driver.find_elements_by_tag_name('a')
    
    hrefs = []
    for link in links:
        hyperlink = link.get_attribute('href')
        if hyperlink != None and 'google' not in hyperlink:
            hrefs.append(hyperlink)

    # FIXME: get more articles than are just on the first page

    driver.close()

    return hrefs


def getArticleInfo(url):
    '''
    Gets the text of a given article
    
    Keyword Arguments:
    url -- The URL for the article to parse

    return -- Article object w/ both title and text of article at url
    '''
    article = newspaper.Article(url)

    try:
        article.download()
    except:
        pass

    article.parse()

    return Article(article.title, article.text)


def getArticles(urls):
    '''
    Iterates over all of the articles and parses them

    Saves the text of each article in a list of articles

    Keyword Arguments:
    urls -- The list of URLs pointing to articles

    return -- List of text from each article
    '''
    articles = []
    for url in urls:
        articles.append(getArticleInfo(url))

    return articles


def extractNumbers(articleList, classificationList, c, dataset):
    for article in articleList:
        title = article.getTitle()
        text = article.getText()

        blob0 = TextBlob(title)
        blob1 = TextBlob(text)

        titlePol = blob0.sentiment.polarity
        textPol = blob1.sentiment.polarity

        dataset.append([titlePol, textPol])
        classificationList.append(c)


def getData():
    '''
    Collects and aggregates data for train/test purposes

    return -- the aggregate feature dataset and accompanying classifications
    ''''
    positiveURLs = getArticleURLS('optimistc news about coronavirus')
    negativeURLs = getArticleURLS('coronavirus news getting worse')

    positiveArticles = getArticles(positiveURLs)
    negativeArticles = getArticles(negativeURLs)

    positiveDataset = []
    negativeDataset = []
    classification = []

    extractNumbers(positiveArticles, classification, 0, positiveDataset)
    extractNumbers(negativeArticles, classification, 1, negativeDataset)

    # Join the datasets together to create the data which will be trained/tested on
    dataset = positiveDataset.append(negativeDataset)

    return dataset, classification


def trainModel():
    '''
    Trains model based on data

    return -- the model itself for prediction purposes
    '''
    dataset, classification = getData()

    gnb = GaussianNB()

    # Split the training and testing data
    x_train, x_test, y_train, y_test = \
        train_test_split(dataset, classification, test_size=0.5)        # FIXME: might want to try something besides 50/50 split

    model = gnb.fit(x_train, y_train)

    return model


def filterArticles(urls):
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
        # conduct sentiment analysis
        # run machine learning algorithm on the polarity of the sentiment analysis as the classifying number
        # if positive article, add to list of positives
        title = article.getTitle()
        text = article.getText()

        blob0 = TextBlob(title)
        blob1 = TextBlob(text)
        print('title sentiment: ', blob0.sentiment.polarity)
        print('text sentiment: ', blob1.sentiment.polarity)

        currPair = [blob0.sentiment.polarity, blob1.sentiment.polarity]

        if blob1.sentiment.polarity > 0:
            positiveArticleURLs.append(urls[index])

        index += 1

    return positiveArticleURLs


if __name__ == '__main__':
    model = trainModel()
    '''urls = getArticleURLS('optimistic news about coronavirus')
    pprint(urls)
    urls = [urls[0]]
    positiveArticles = filterArticles(urls)

    pprint(positiveArticles)'''

    # filteredList = filterArticles(articles)

    # Get a bunch of articles from the internet about coronavirus
    # Iterate over each article, classifying it as good or bad
        # If good, add it to the growing list of good articles
    # chron-esque job to craft email and then send once per week, day, month, etc. (using twilio)