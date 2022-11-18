'''
Card Class

A class representing a playing card
'''
from enums import Suit, Level
import tkinter as tk
from PIL import Image, ImageTk

cardImageDirectory = "/home/richawil/Documents/Programming/Apps/Cards/images/"
cardBackPortrait = cardImageDirectory + "cardBack_p.png"
cardBackLandscape = cardImageDirectory + "cardBack_l.png"

class Card():

    def __init__(self, suit, level):
        self.suit = suit
        self.level = level
        self.position = None
        # GUI variables
        self.portraitFile, self.landscapeFile = self.getCardFileNames()
        self.faceUp = False
        self.anchor = [0, 0]
        self.canvas = None
        self.image = None

    def getCardLevel(self, card):
        return card.level.value
        
    def toStr(self):
        if self.level.value == 1 or self.level.value == 14:
            outStr = "Ace of "
        else:
            outStr = self.level.name + " of "
        if self.suit == Suit.SPADE:
            outStr += 'Spades'
        elif self.suit == Suit.HEART:
            outStr += 'Hearts'
        elif self.suit == Suit.DIAMOND:
            outStr += 'Diamonds'
        elif self.suit == Suit.CLUB:
            outStr += 'Clubs'
        else:
            outStr += 'Unknown' 
        return outStr

    def show(self):
        print("{}".format(self.toStr()))

    # GUI Methods
    @staticmethod
    def getBackImage():
        return cardBackImageFile

    def getCardFileNames(self):
        fileName = cardImageDirectory
        if self.level.value == 1 or self.level.value == 14:
            fileName += "ace_of_"
        elif self.level.value > 1 and self.level.value < 11:
            fileName += str(self.level.value) + "_of_"
        elif self.level.value == 11:
            fileName += "jack_of_"
        elif self.level.value == 12:
            fileName += "queen_of_"
        elif self.level.value == 13:
            fileName += "king_of_"
        else:
            fileName += 'Unknown_level' 
            
        if self.suit == Suit.SPADE:
            fileName += 'spades'
        elif self.suit == Suit.HEART:
            fileName += 'hearts'
        elif self.suit == Suit.DIAMOND:
            fileName += 'diamonds'
        elif self.suit == Suit.CLUB:
            fileName += 'clubs'
        else:
            fileName += 'Unknown_suit'
        portraitName = fileName + '_p.png'
        landscapeName = fileName + '_l.png'
        return portraitName, landscapeName

    
    # Rotation is in degrees in the counterclockwise direction
    def getCardImage(self, rotation):
        #print("Getting image for card {}".format(card.toStr()))
        # Open the card image file
        if self.faceUp:
            if rotation == 0:
                card_img = Image.open(self.portraitFile)
            elif rotation == 90:
                card_img = Image.open(self.landscapeFile)
            else:
                print("Unsupported rotation value of {}".format(rotation))
        else:
            if rotation == 0:
                card_img = Image.open(cardBackPortrait)
            elif rotation == 90:
                card_img = Image.open(cardBackLandscape)
            else:
                print("Unsupported rotation value of {}".format(rotation))
        self.image = ImageTk.PhotoImage(card_img)
        return self.image

    '''      
    Anchor position is one of n, ne, e, se, s, sw, w, nw, or center
    The position indicates the location of the anchor point relative
    to the image
    So a position of se will put the south east point of the image on
    the anchor point
    '''
    def setGuiParams(self, canvas, x, y):
        self.anchor = [x, y]
        self.canvas = canvas
