"""
Author: Jake Wachs
Date: 04/02/2020

Beacon - COVID-19 optimism bot
"""
from ml import trainModel, filterArticles, testmodel
from web import getArticleURLS
from util import craftMsg
from util import sendEmails
from web import checkRecoveries
import auth

import time

if __name__ == '__main__':
    '''
    model, x_test, y_test = trainModel()
    testmodel(model, x_test, y_test)
    '''
    
    '''
    urls = getArticleURLS('optimistic news about coronavirus', 1)
    positiveArticles = filterArticles(urls, model)
    msg = craftMsg(positiveArticles)
    sendEmails(auth.mailingList, msg)
    '''

    lastRecovered = checkRecoveries(0)

    model, x_test, y_test = trainModel()

    WAIT_TIME = 86400       # 24 hours
    while True:
        recoveredDifference = checkRecoveries(lastRecovered)
        print('recovered difference', recoveredDifference)

        if recoveredDifference >= 10000:
            lastRecovered = checkRecoveries(0)
    
            urls = getArticleURLS('optimistic news about coronavirus', 1)
            positiveArticles = filterArticles(urls, model)

            msg = craftMsg(positiveArticles)
            sendEmails(auth.mailingList, msg)
        
        time.sleep(WAIT_TIME)
