'''
Author: Jake Wachs
Date: 06 April 2020

The Article class
'''

class Article:
    def __init__(self, title, text, img):
        '''
        Default constructor

        Keyword Arguments:
        title -- new title
        text -- new text
        '''
        self.title = title
        self.text = text
        self.img = img

    
    def setTitle(self, t):
        '''
        Setter for the title attribute

        Keyword Arguments:
        t -- new title
        '''
        self.title = t

    
    def getTitle(self):
        '''
        Getter for the title attribute

        return -- article's title
        '''
        return self.title


    def setText(self, t):
        '''
        Setter for the text attribute

        Keyword Arguments:
        t -- new text
        '''
        self.text = t

    
    def getText(self):
        '''
        Getter for the text attribute

        return -- the text of the article
        '''
        return self.text

    
    def setImg(self, img):
        '''
        Setter for the img attribute

        Keyword Arguments:
        img -- article's top image
        '''
        self.img = img


    def getImg(self):
        '''
        Getter for the img attribute

        return -- top image of the article
        '''
        return self.img