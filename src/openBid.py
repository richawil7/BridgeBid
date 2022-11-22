'''
Functions used for generating bids
'''

from enums import Suit, Level, DistMethod
from utils import *
from card import Card
from cardPile import CardPile
    
def calcOpenBid(hand):
    (hcPts, lenPts) = hand.evalHand(DistMethod.LONG)
    totalPts = hcPts + lenPts

    # Find the longest suit
    (numCards, bidSuit) = hand.findLongestSuit()
    
    # Check if we should open weak with a long suit
    if totalPts < 13:
        bidLevel = numCards - 4
        return (bidLevel, bidSuit)

    # Check for balanced hand
    if hand.isHandBalanced():
        if hcPts >= 15 and hcPts <= 17:
            return (1, Suit.NOTRUMP)
        # Does hand have stoppers in all 4 suits
        if hand.hasStoppers():
            if hcPts >= 18 and hcPts <= 19:
                return (1, Suit.bidSuit)
            if hcPts >= 20 and hcPts <= 21:
                return (2, Suit.NOTRUMP)
            if hcPts >= 25 and hcPts <= 27:
                return (3, Suit.NOTRUMP)
            if hcPts >= 28 and hcPts <= 29:
                return (4, Suit.NOTRUMP)

    # If you get here, the hand is unbalanced
    # Check for a big hand
    if totalPts >= 22:
        return (2, Suit.CLUB)
    # Check for a long suit
    if numCards >= 5:
        return (1, bidSuit)
    # Bid the longer minor
    bidSuit = findLongerMinor(hand)
    return (1, bidSuit)
    
    print("bid: calcOpenBid: did not find bid")        
    print("calcOpenBid: hcPts=%d lenPts=%d suit=%s suitLen=%d" % (hcPts, lenPts, bidSuit.name, numCards))
            
