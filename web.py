"""
Author: Jake Wachs
Date: 04/20/2020

Web scraping and other web related functions
"""

from classes.Article import Article
from util import extractNumbers

from datetime import date
import time
import csv
from selenium import webdriver  # FIXME: does Google have an API I can use instead of Selenium
from selenium.webdriver.common.keys import Keys
import newspaper
import requests

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


def getArticleURLS(query, numPages):
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

    nextXpath = '/html/body/div[6]/div[3]/div[8]/div[1]/div[2]/div/div[5]/div[2]/span[1]/div/table/tbody/tr/td[12]/a/span[2]'

    hrefs = []
    for i in range(0,numPages):
        # time.sleep(1)
        currURLs = getPageURLS(driver)
        hrefs = hrefs + currURLs
        try:
            nextBtn = driver.find_element_by_xpath(nextXpath)   # if there's no next page, break
            nextBtn.click()
        except:
            break

        if numPages == 1:
            break

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
    i = 0
    numArticles = len(urls)
    articles = []
    for url in urls:
        print('Getting article ', i, ' out of ', numArticles, '(', i/numArticles, ')')
        articles.append(getArticleInfo(url))
        i = i + 1

    return articles


def scrapeData():
    '''
    Collects and aggregates data for train/test purposes

    return -- the aggregate feature dataset and accompanying classifications
    '''
    print('GETTING DATA...')
    positiveURLs = getArticleURLS('optimistc news about coronavirus', 100)
    negativeURLs = getArticleURLS('coronavirus news getting worse', 100)

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

    fp = open('log.txt', 'a')
    fp.write('Total recovered is: ' + str(totalRecovered) + '\n')
    fp.close()

    return totalRecovered - prevNum