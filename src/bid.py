'''
Functions used for generating bids
'''

from enums import Suit, Level, CardPosition, DistMethod
from utils import *
from card import Card
from cardPile import CardPile



# We might not be able to take all the high cards winners we have
# if our opponents run out of this suit.
# This function returns the maximum number of times this suit will "go around"
def getMaxGoRounds(suit, suitStats, cardCount):
    numOutstandingCards = 13 - cardCount
    if numOutstandingCards >= 9:
        # Suit could go around up to 3 times
        return 3
    elif numOutstandingCards >= 6:
        # This suit will only go around twice at best
        #print("%s will at best only go around two times".format(suit.name))
        return 2
    elif numOutstandingCards >= 3:
        # This suit will only go around once at best
        #print("%s will at best only go around one time".format(suit.name))
        return 1
    elif numOutstandingCards < 3:
        # This suit get trumped immediately
        #print("%s will not go around even 1 time".format(suit.name))
        return 0



'''
Function to calculate a bid.
Inputs:
    table - card table object
    origHand - hand on which to perform the calculation (read-only)
Outputs:
    distribution - distribution of suits in the hand
    handStats - counts of cards in each category
Returns:
    bid - the actual bid
'''    
def calcBid(table, origHand, distribution, handStats):

    return (2, Suit.DIAMOND)
