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

def getArticleURLS():
    '''
    Gets list of good news article URLs about COVID-19

    Automatically Googles good news articles about COVID-19 and returns
    a list of those articles' URLs

    return -- list of URLs of articles
    '''
    driver = webdriver.Firefox()
    driver.get('https://www.google.com')

    que = driver.find_element_by_xpath("//input[@name='q']")
    que.send_keys('good positive news about coronavirus')
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
        if blob1.sentiment.polarity > 0:
            positiveArticleURLs.append(urls[index])

        index += 1

    return positiveArticleURLs


if __name__ == '__main__':
    urls = getArticleURLS()
    pprint(urls)
    urls = [urls[0]]
    positiveArticles = filterArticles(urls)

    pprint(positiveArticles)

    # filteredList = filterArticles(articles)

    # Get a bunch of articles from the internet about coronavirus
    # Iterate over each article, classifying it as good or bad
        # If good, add it to the growing list of good articles
    # chron-esque job to craft email and then send once per week, day, month, etc. (using twilio)