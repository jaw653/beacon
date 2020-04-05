"""
Author: Jake Wachs
Date: 04/02/2020

Beacon - A shining light in the storm
"""

import time
from pprint import pprint       # FIXME: just for testing purposes
import requests
from selenium import webdriver
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
        hrefs.append(link.get_attribute('href'))

    # FIXME: get each article up to 100, 1000, etc. using xpaths (like above)

    driver.close()

    return hrefs


def getArticleText():
    pass


def trimArticles(articles):
    '''
    Removes negative or indifferent articles from the list

    Keyword Arguments:
    articles -- list of articles from original Google search

    return -- refined list of articles with only positive documents
    '''
    pass


if __name__ == '__main__':
    urls = getArticleURLS()
    pprint(urls)
    # refinedList = trimArticles(articles)

    # Get a bunch of articles from the internet about coronavirus
    # Iterate over each article, classifying it as good or bad
        # If good, add it to the growing list of good articles
    # chron-esque job to craft email and then send once per week, day, month, etc. (using twilio)