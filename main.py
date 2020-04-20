"""
Author: Jake Wachs
Date: 04/02/2020

Beacon - COVID-19 optimism bot
"""
from ml import trainModel

import time
from pprint import pprint       # FIXME: just for testing purposes



if __name__ == '__main__':
    model, x_test, y_test = trainModel()
    '''urls = getArticleURLS('optimistic news about coronavirus', 1)
    positiveArticles = filterArticles(urls, model)
    msg = craftMsg(positiveArticles)
    sendEmails(auth.mailingList, msg)'''
'''
    lastRecovered = checkRecoveries(0)

    model, x_test, y_test = trainModel()

    WAIT_TIME = 86400       # 24 hours
    while True:
        recoveredDifference = checkRecoveries(lastRecovered)

        if recoveredDifference >= 10000:
            lastRecovered = checkRecoveries(0)
    
            urls = getArticleURLS('optimistic news about coronavirus', 1)
            positiveArticles = filterArticles(urls, model)

            msg = craftMsg(positiveArticles)
            sendEmails(auth.mailingList, msg)
        
        time.sleep(WAIT_TIME)
'''