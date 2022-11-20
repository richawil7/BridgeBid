'''
Functions used for generating bids
'''

from enums import Suit, Level, DistMethod
from utils import *
from card import Card
from cardPile import CardPile

def stubBid(table, bidsList):
    if len(bidsList) > 0:
        bidTuple = bidsList[-1]
        lastBidLevel = bidTuple[0]
        nextBidLevel = lastBidLevel + 1
        lastBidSuit = bidTuple[1]
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

def canIOpen(hand, competition, seatNum):
    (hcPts, lenPts) = hand.evalHand(DistMethod.LONG)
    totalPts = hcPts + lenPts 
    if totalPts >= 14:
        return True

    # Get number of cards in the longest 2 suits
    (numCardsLongest, numCardsNextLongest) = hand.numCardsInTwoLongestSuits()

    # Can open with the rule of 20
    if hcPts + numCardsLongest + numCardsNextLongest >= 20:
        return True

    # Check if we can open due to length
    # Find the longest suit
    (numCards, longestSuit) = hand.findLongestSuit()
    if numCards < 6:
        return False

    if longestSuit == Suit.CLUB:
        return False
    
    # Check the strength of the longest suit
    numHighCards = hand.evalSuitStrength(longestSuit)
    if numHighCards <= 1:
        return False

    # Check the number of cards in the next longest suit
    if numCardsNextLongest >= 4:
        return False

    return True
    

def calcOpenBid(hand):
    (hcPts, lenPts) = hand.evalHand(DistMethod.LONG)
    totalPts = hcPts + lenPts

    # Find the longest suit
    (numCards, bidSuit) = hand.findLongestSuit()
    
    # Check if we should open weak with a long suit
    if totalPts < 13:
        bidLevel = numCards - 4
        return (bidLevel, bidSuit)

    # Check for unbalanced hand
    if not hand.isHandBalanced():
        # Check for a big hand
        if totalPts >= 22:
            return (2, Suit.CLUB)
        
        if numCards >= 5:
            return (1, bidSuit)

        # Bid the longer minor
        numDiamonds = hand.getNumCardsInSuit(Suit.DIAMOND)
        numClubs = hand.getNumCardsInSuit(Suit.CLUB)
        if numDiamonds > numClubs:
            return (1, Suit.DIAMOND)
        elif numClubs > numDiamonds:
            return (1, Suit.CLUB)
        elif numDiamonds == 4:
            return (1, Suit.DIAMOND)
        elif numClubs == 3:
            return (1, Suit.CLUB)

    # This is a balanced hand
    if hcPts >= 15 and hcPts <= 17:
        return (1, Suit.NOTRUMP)
    if hcPts >= 18 and hcPts <= 19:
        return (1, Suit.bidSuit)
    if hcPts >= 20 and hcPts <= 21:
        return (2, Suit.NOTRUMP)
    if hcPts >= 25 and hcPts <= 27:
        return (3, Suit.NOTRUMP)
    if hcPts >= 28 and hcPts <= 29:
        return (4, Suit.NOTRUMP)
    
        
            
    
