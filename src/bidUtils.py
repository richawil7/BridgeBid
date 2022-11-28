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
    (suit1, numCardsLongest, suit2, numCardsNextLongest) = hand.numCardsInTwoLongestSuits()

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

def getHintForOpener():
    hintStr = "<6 pts: Pass\n<13 pts\n\t>=6 strong\n\t\tTwo 4+ suit:pass\n\t\tLen-4\nBalanced\n\t15-17: 1NT\n\tStop all suits\n\t\t18-19 hcp: 1L and jump NT\n\t\t20-21 hcp: 2NT\n\t\t25-27 hcp: 3NT\n\t\t28-29 hcp: 4NT\n22+ pts: 2C\nRule of 20:\n\tMajor 5+5: 1S\n\tMajor 4+4: 1H\n\tLong major: 1L\n\tMinor 4+4: 1D\n\tMinor 3+3: 1C\n\tLong minor: 1L"
    return hintStr

def getHintForResponder(level, openSuit):
    if level == 1:
        if openSuit == Suit.CLUB or openSuit == Suit.DIAMOND:
            hintStr = getHintForRespond1Minor()
        elif openSuit == Suit.HEART or openSuit == Suit.SPADE:
            hintStr = getHintForRespond1Major()
        elif openSuit == Suit.NOTRUMP:
            hintStr = getHintForRespond1NT()
    elif level == 2:        
        if openSuit == Suit.CLUB:
            hintStr = getHintForRespond2Club()
    return hintStr


def getHintForRespond1Minor():
    hintStr = "<6 pts: Pass\n4 card major:\n\tMajor 5+5: 1S\n\tMajors 4+4: 1H\n4 card support\n\t6-9 pts: raise\n\t10-11 pts: jump\n\t12+: new suit\n10+ pts\n\tUnbid stoppers\n\t\t16-18 pts: 3NT\n\t\t13-15 pts: 2NT\n\t5+5: higher\n\t4+4: lower\n\tLongest\n4+D over 1C: 1D\n1NT"
    return hintStr

def getHintForRespond1Major():
    hintStr = "<6 pts: Pass\n3+ support\n\t6-9 pts\n\t\t5+ support and single/void: 4B\n\t\t2B\n\t10-11 pts: 2B\n\tNew suit\n4+S over 1H: 1S\n10+ pts\n\t4+ H 2H\n\tUnbid stoppers\n\t\t16-18 pts: 3NT\n\t\t13-15 pts: 2NT\n\t5+5: higher\n\t4+4: lower\n\tLongest\n1NT"
    return hintStr

def getHintForRespond1NT():
    hintStr = "<8 pts\n\t5+ (exc C): 2L\n\tPass\nBalanced and no 4+ major: nNT (2,3,4,6,5,7)\n6+ major and 10-15 pts: 4L\n6+ minor: 3NT\n4 major: 2C\n5+ suit and 10 pts: 3L\n5+ major and 8-9 pts: 2C\nnNT (n=2,3,4,6,5,7)"
    return hintStr


def getHintForOpenerRebid():
    hintStr = "Here is the hint for an opener rebid\n"
    return hintStr

def getHintForResponderRebid():
    hintStr = "Here is the hint for an responder rebid\n"
    return hintStr
