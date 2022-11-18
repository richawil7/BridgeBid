'''
Functions used for generating bids
'''

from enums import Suit, Level, DistMethod
from utils import *
from card import Card
from cardPile import CardPile



'''
Function to calculate a bid.
Inputs:
    table - card table object
    origHand - hand on which to perform the calculation (read-only)
Returns:
    bid - the actual bid
'''    
def calcBid(table, hand, bidsList):
    print("bid: calcBid entry")
    if len(bidsList) > 0:
        print("List of bids so far: %s" % bidsList)
        bidTuple = bidsList[-1]
        lastBidLevel = bidTuple[0]
        nextBidLevel = lastBidLevel + 1
        lastBidSuit = bidTuple[1]
        print("Last bid was %d of %s" % (lastBidLevel, lastBidSuit.name))
        if lastBidSuit == Suit.NOTRUMP:
            nextBidSuit = Suit.CLUB
        elif lastBidSuit == Suit.HEART:
            nextBidSuit = Suit.SPADE
        else:
            nextBidSuit = Suit.HEART
    else:
        # First bid
        nextBidLevel = 1
        nextBidSuit = Suit.CLUB

    return (nextBidLevel, nextBidSuit)
