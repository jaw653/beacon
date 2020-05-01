"""
Author: Jake Wachs
Date: 04/20/2020

Mostly logic based utility functions
"""
from classes.Article import Article

import smtplib, ssl             # for sending emails
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from textblob import TextBlob   # for sentiment analysis
import auth
from datetime import date, datetime

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
                the pandemic to brighten your day (I'm just a robot, please bear with me if some of
                these articles are not what you expect!):</p>
                </br>
                </br>
    '''

    for url in urls:
        msg = msg + '</br></br><p>' + str(url) + '</p>'

    msg = msg + '<p>+++++I AM A ROBOT, PLEASE DO NOT REPLY+++++</p></body></html>'

    return msg


def sendEmails(mailingList, msg):               # FIXME: craft message with links and pass in here
    sslContext = ssl.create_default_context()

    senderEmail = 'beaconapp.hope@gmail.com'

    server = smtplib.SMTP_SSL('smtp.gmail.com', 465, context=sslContext)
    server.login(senderEmail, auth.password)

    payload = MIMEText(msg, 'html')
    message = MIMEMultipart()
    message['From'] = senderEmail
    message['To'] = subscriber
    message['Subject'] = '10,000 More Recover from COVID-19'
    message.attach(payload)

    msgString = message.as_string()

    for subscriber in mailingList:          # FIXME: just craft one email, not one per subscriber
        server.sendmail(senderEmail, subscriber, msgString)


def logOutput(emailSent, recovDiff):
    '''
    Logs the performance of the script to log.txt

    Keyword Arguments:
    emailSent -- bool if emails should have been sent

    recovDiff -- the delta of # people recovered from CV-19
    '''
    today = date.today()
    formattedDate = '{:02d}'.format(today.month) + '-' + \
        '{:02d}'.format(today.day) + '-' + str(today.year)


    fp = open('log.txt', 'a')
    fp.write(str(datetime.now()) + '\n')
    fp.write('Recovered difference: ' + str(recovDiff) + '\n')
    fp.write('Email sent: ' + str(emailSent) + '\n')
    fp.write('--------------------------------------------------------------------------------\n\n')

    fp.close()