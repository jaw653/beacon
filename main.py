"""
Author: Jake Wachs
Date: 04/02/2020

Beacon - COVID-19 optimism bot
"""

from classes.Article import Article
import auth

import newspaper
import sched, time
from datetime import date
import os
from pprint import pprint       # FIXME: just for testing purposes
import requests
from textblob import TextBlob   # for sentiment analysis
from selenium import webdriver  # FIXME: does Google have an API I can use instead of Selenium
from selenium.webdriver.common.keys import Keys
import smtplib, ssl             # for sending emails
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import csv

from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import GaussianNB


def getPageURLS(driver):
    '''
    Gets all of the URLs on a page
    '''
    links = driver.find_elements_by_tag_name('a')
    
    hrefs = []
    for link in links:
        hyperlink = link.get_attribute('href')
        if hyperlink != None and 'google' not in hyperlink:
            hrefs.append(hyperlink)

    return hrefs


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
    time.sleep(1)

    nextXpath = '/html/body/div[6]/div[2]/div[9]/div[1]/div[2]\
        /div/div[5]/div[2]/span[1]/div/table/tbody/tr/td[12]/a/span[2]'

    hrefs = []
    for i in range(0,1):
        # time.sleep(1)
        currURLs = getPageURLS(driver)
        hrefs = hrefs + currURLs
        nextBtn = driver.find_element_by_xpath(nextXpath)
        nextBtn.click()

    print(hrefs)

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
        res = requests.get(url, timeout=5).text
    except:
        res = None

    if res != None:      # Litmus test to see if forbidden from scraping site
        try:
            article.download()
            article.parse()
            print('PARSED ARTICLE: ', article.title)

            return Article(article.title, article.text)
        except:
            return None


    else:
        return None         # FIXME: if this is an issue, just return Article('neutral', 'neutral')


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

    Keyword Arguments:
    articleList -- list of Article objects

    classificationList -- empty list to append 0 or 1 on

    c -- classification of current article (0 or 1)

    return -- the dataset of polarities
    '''
    i = 0
    dataset = []
    for article in articleList:
        if article != None:         # FIXME: change != to not
            print('Conducting SA on article: ', article.getTitle())

            title = article.getTitle()
            text = article.getText()

            i = i + 1

            blob0 = TextBlob(title)
            blob1 = TextBlob(text)

            titlePol = blob0.sentiment.polarity
            textPol = blob1.sentiment.polarity

            dataset.append([titlePol, textPol])
            classificationList.append(c)

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


def getReport():
    '''
    Gets the open CSV data from JHU github

    return -- raw data HTTP response
    '''
    today = date.today()
    formattedDate = '{:02d}'.format(today.month) + '-' + '{:02d}'.format(today.day) + '-' + str(today.year)

    reportLink0 = ('https://raw.githubusercontent.com/CSSEGISandData/COVID-19/'
        'master/csse_covid_19_data/csse_covid_19_daily_reports/')
    reportLink1 = reportLink0 + formattedDate + '.csv'

    res = requests.get(reportLink1)
    if res.status_code == 404:
        formattedDate = '{:02d}'.format(today.month) + '-' + '{:02d}'.format(today.day-1) + '-' + str(today.year)       # FIXME: edge case of first day of new month, need to subtract the month instead of day
        newLink = reportLink0 + formattedDate + '.csv'
        res = requests.get(newLink)

    return res


def checkRecoveries(prevNum):
    '''
    Checks the JHU CV dashboard for number recovered

    Keyword Arguments:
    prevNum -- the previous number recovered

    return -- the difference between last time and this time of num recovered
    '''
    rawReport = getReport().text

    # print(rawReport)

    lines = rawReport.splitlines()
    data = csv.reader(lines)
    # print(data)
    totalRecovered = 0
    for row in data:
        if row[9].isdigit():
            totalRecovered = totalRecovered + int(row[9])

    print(totalRecovered)

    return totalRecovered - prevNum


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
        if len(line) > 2:
            listElement = []
            line = line.split(',')
            for token in line:
                if token[0] == '[':
                    token = token[1:len(token)]   # strip bracket from number
                elif token[len(token)-1] == '\n':
                    token = token[0:len(token)-3]   # -3 b/c of trailing newline and bracket

                listElement.append(float(token))

            print('this should be a 2 value list: ', listElement)
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
        train_test_split(dataset, classification, test_size=0.3)        # FIXME: might want to try something besides 50/50 split

    model = gnb.fit(x_train, y_train)

    print('MODEL TRAINED.')
    return model, x_test, y_test


def testModel(model, x_test, y_test):
    '''
    Tests model accuracy; for testing purposes only
    '''
    print('TESTING MODEL...')
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

        if model.predict([currPair]) == 0:                    # FIXME: replace this with MACHINE LEARNING!!!
            positiveArticleURLs.append(urls[index])
        else:
            print('ARTICLE ', article.getTitle(), ' FLAGGED AS NEGATIVE')

        index += 1

    return positiveArticleURLs


def craftMsg(urls):
    '''
    Takes the urls of positive articles and converts to proper string
    
    Keyword Arguments:
    urls -- the urls of positive articles

    return -- proper html string of message
    '''
    msg = '''\
        <html>
            <head></head>
            <body>
                <p>Hi from Beacon!</p>
                </br>
                </br>
                <p>If you're getting this message, it means that 10,000 more people recovered
                from COVID-19! That's 10,000 more lives saved. Here's some optimistic news about
                the pandemic to brighten your day:</p>
                </br>
                </br>
    '''

    for url in urls:
        msg = msg + '</br></br>' + str(url)

    msg = msg + '<p>+++++I AM A ROBOT, PLEASE DO NOT REPLY+++++</p></body></html>'

    return msg


def sendEmails(mailingList, msg):               # FIXME: craft message with links and pass in here
    sslContext = ssl.create_default_context()

    senderEmail = 'beaconapp.hope@gmail.com'

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=sslContext)
    server.login(senderEmail, auth.password)

    payload = MIMEText(msg, 'html')

    for subscriber in mailingList:
        message = MIMEMultipart()
        message['From'] = senderEmail
        message['To'] = subscriber
        message['Subject'] = '10,000 More Recover from COVID-19'
        message.attach(payload)
        server.sendmail(senderEmail, subscriber, message.as_string())


if __name__ == '__main__':
    model, x_test, y_test = trainModel()
    urls = getArticleURLS('optimistic news about coronavirus')
    positiveArticles = filterArticles(urls, model)
    msg = craftMsg(positiveArticles)
    sendEmails(auth.mailingList, msg)
'''
    lastRecovered = checkRecoveries(0)

    model, x_test, y_test = trainModel()

    WAIT_TIME = 86400       # 24 hours
    while True:
        recoveredDifference = checkRecoveries(lastRecovered)

        if recoveredDifference >= 10000:
            lastRecovered = checkRecoveries(0)
    
            urls = getArticleURLS('optimistic news about coronavirus')
            positiveArticles = filterArticles(urls, model)

            msg = craftMsg(positiveArticles)
            sendEmails(auth.mailingList, msg)
        
        time.sleep(WAIT_TIME)
'''