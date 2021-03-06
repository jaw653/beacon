"""
Author: Jake Wachs
Date: 04/02/2020

Beacon - COVID-19 optimism bot
"""
from ml import trainModel, filterArticles, testmodel
from web import getArticleURLS
from util import craftMsg, sendEmails, logOutput
from web import checkRecoveries
import auth

import time
from datetime import date

if __name__ == '__main__':
    # model, dataset, classification = trainModel()

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
    
    lastRecovered = checkRecoveries()

    model, x_test, y_test = trainModel()

    WAIT_TIME = 86400       # 24 hours
    # WAIT_TIME = 600       # 10 minutes
    while True:
        currRecovered = checkRecoveries()
        recoveredDifference = currRecovered - lastRecovered
        # print('recovered difference', recoveredDifference)

        emailSent = False
        if recoveredDifference >= 10000:
            lastRecovered = currRecovered
    
            urls = getArticleURLS('optimistic news about coronavirus', 1)
            positiveArticles = filterArticles(urls, model)

            msg = craftMsg(positiveArticles)
            try:
                sendEmails(auth.mailingList, msg)
                emailSent = True
            except:
                emailSent = False

        logOutput(emailSent, recoveredDifference)
        
        time.sleep(WAIT_TIME)
    