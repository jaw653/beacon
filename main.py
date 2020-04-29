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
    
    lastRecovered = checkRecoveries(0)

    model, x_test, y_test = trainModel()

    WAIT_TIME = 86400       # 24 hours
    while True:
        recoveredDifference = checkRecoveries(lastRecovered)
        # print('recovered difference', recoveredDifference)

        emailSent = False
        if recoveredDifference >= 10000:
            emailSent = True
            lastRecovered = checkRecoveries(0)
    
            urls = getArticleURLS('optimistic news about coronavirus', 1)
            positiveArticles = filterArticles(urls, model)

            msg = craftMsg(positiveArticles)
            sendEmails(auth.mailingList, msg)

        logOutput(emailSent, recoveredDifference)
        
        time.sleep(WAIT_TIME)
    