"""
Author: Jake Wachs
Date: 04/02/2020

Beacon - A shining light in the storm
"""

from classes.Article import Article
import auth

import newspaper
import time
import os
from pprint import pprint       # FIXME: just for testing purposes
import requests
from textblob import TextBlob   # for sentiment analysis
from selenium import webdriver  # FIXME: does Google have an API I can use instead of Selenium
from selenium.webdriver.common.keys import Keys
import smtplib, ssl             # for sending emails
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

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

    if requests.get(url).text != None:      # Litmus test to see if forbidden from scraping site
        article.download()

        print('PARSING ARTICLE')
        article.parse()

        return Article(article.title, article.text)
    else:
        return None


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


def extractNumbers(articleList, classificationList, c):
    '''
    Conducts sentiment analysis on each article in the given article list
    '''
    i = 0
    dataset = []
    for article in articleList:
        print('Conducting SA on article ', i)

        title = article.getTitle()
        text = article.getText()

        i = i + 1

        blob0 = TextBlob(title)
        blob1 = TextBlob(text)

        titlePol = blob0.sentiment.polarity
        textPol = blob1.sentiment.polarity

        dataset.append([titlePol, textPol])
        classificationList.append(c)
        print('dataset is now:')
        print(dataset)

    return dataset


def scrapeData():
    '''
    Collects and aggregates data for train/test purposes

    return -- the aggregate feature dataset and accompanying classifications
    '''
    print('GETTING DATA...')
    positiveURLs = getArticleURLS('optimistc news about coronavirus')
    negativeURLs = getArticleURLS('coronavirus news getting worse')

    positiveArticles = getArticles(positiveURLs)
    negativeArticles = getArticles(negativeURLs)

    classification = []

    positiveDataset = extractNumbers(positiveArticles, classification, 0)
    negativeDataset = extractNumbers(negativeArticles, classification, 1)

    '''print('positive dataset is:')
    print(positiveDataset)
    print('negativeDataset is: ')
    print(negativeDataset)'''

    # Join the datasets together to create the data which will be trained/tested on
    dataset = positiveDataset + negativeDataset

    with open('data.txt', 'w') as fp:
        for item in dataset:
            fp.write('%s\n' % item)
    fp.close()

    with open('classification.txt', 'w') as fp1:
        for item in classification:
            fp1.write('%s\n' % item)
    fp1.close()

    return dataset, classification


def readData(filename):
    '''
    Reads polarity data from a file instead of scraping the web

    Keyword Arguments:
    filename -- Name of the file to be read from

    return -- List from given file
    '''
    dataList = []

    fp = open(filename, 'r')

    line = fp.readline()
    while line:
        if len(line) > 1:
            listElement = []
            line = line.split(',')
            for token in line:
                if token[0] == '[':
                    token = token[1:len(token)]   # strip bracket from number
                elif token[len(token)-1] == '\n':
                    token = token[0:len(token)-3]   # -3 b/c of trailing newline and bracket

                print('appending ', float(token), ' to listElement')
                listElement.append(float(token))

            print('final list element is: ', listElement)
            dataList.append(listElement)
        
        else:
            dataList.append(int(line))
        
        line = fp.readline()

    fp.close()

    return dataList


def readLists():
    '''
    Reads feature file and classification file and returns data
    
    return -- Dataset and classification lists
    '''
    dataset = readData('data.txt')
    classification = readData('classification.txt')

    return dataset, classification


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
        train_test_split(dataset, classification, test_size=0.5)        # FIXME: might want to try something besides 50/50 split

    model = gnb.fit(x_train, y_train.ravel())

    print('MODEL TRAINED.')
    return model, x_test, y_test


def testModel(model, x_test, y_test):
    '''
    Tests model accuracy; for testing purposes only
    '''
    print('TESTING MODEL...')
    y_predict = model.predict(x_test)
    print('predicted:')
    print(y_predict)

    print('y_test is:')
    print(y_test)
    print('y_predict is:')
    print(y_predict)

    i = 0
    truePos = 0
    trueNeg = 0
    falsePos = 0
    falseNeg = 0
    for prediction in y_predict:
        if prediction == 0:
            if y_test[i] == 0:
                truePos = truePos + 1
            else:
                falsePos = falsePos + 1
        else:
            if y_test[i] == 1:
                trueNeg = trueNeg + 1
            else:
                falseNeg = falseNeg + 1
        i = i + 1

        # FIXME: Print the truth matrix calculated above!!!

    print('true positives: ', truePos)
    print('true negatives: ', trueNeg)
    print('false positives: ', falsePos)
    print('false negatives: ', falseNeg)



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


def sendEmails(mailingList):
    sslContext = ssl.create_default_context()

    senderEmail = 'beaconapp.hope@gmail.com'
    # senderEmail = 'jawax10@gmail.com'


    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=sslContext)
    server.login(senderEmail, auth.password)

    payload = '''\
        <html>
            <head></head>
            <body>
                <p>Hi guys! This message was sent from python. 
                Working on refining machine learning to filter articles better
                and then you should receive positive emails about coronavirus!</p>
                </br>
                </br>
                <p>Love yah, Jake</p>
                </br>
                </br>
                <p>P.S. You can respond to this email but I probably will not see it</p>
            </body>
        </html>
    '''
    payload = MIMEText(payload, 'html')

    for subscriber in mailingList:
        message = MIMEMultipart()
        message['From'] = senderEmail
        message['To'] = subscriber
        message['Subject'] = 'Hello from Beacon!'
        message.attach(payload)
        server.sendmail(senderEmail, subscriber, message.as_string())


if __name__ == '__main__':
    sendEmails(auth.mailingList)
    
    '''
    model, x_test, y_test = trainModel()
    testModel(model, x_test, y_test)
    '''


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