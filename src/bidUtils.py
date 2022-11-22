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

    writeLog(table, "stubBid: in round %d by %s\n" % (table.roundNum, table.currentPos.name))
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
    (numCards, numHighCards) = hand.evalSuitStrength(longestSuit)
    if numHighCards <= 1:
        return False

    # Check the number of cards in the next longest suit
    if numCardsNextLongest >= 4:
        return False

    return True
    
def findLongerMinor(hand):
    numDiamonds = hand.getNumCardsInSuit(Suit.DIAMOND)
    numClubs = hand.getNumCardsInSuit(Suit.CLUB)
    if numDiamonds > numClubs:
        return Suit.DIAMOND
    elif numClubs > numDiamonds:
        return Suit.CLUB
    elif numDiamonds == 4:
        return Suit.DIAMOND
    elif numClubs == 3:
        return Suit.CLUB
