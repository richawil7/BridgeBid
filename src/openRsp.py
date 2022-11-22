'''
Functions used for generating bids
'''

from enums import Suit, Level, DistMethod
from utils import *
from card import Card
from cardPile import CardPile


def openResponse(table, hand, bidsList):
    writeLog(table, "openResponse: bidsList={}\n".format(bidsList))
    # Extract opening bid from partner
    (openLevel, openSuit) = bidsList[-2]
    writeLog(table, "openResponse: openLevel=%d openSuit=%s\n" % (openLevel, openSuit))
    if openLevel == 1:
        if openSuit == Suit.CLUB or openSuit == Suit.DIAMOND:
            (bidLevel, bidSuit) = openRsp1Minor(hand, openSuit)
        elif openSuit == Suit.HEART or openSuit == Suit.SPADE:
            (bidLevel, bidSuit) = openRsp1Major(hand, openSuit)
        elif openSuit == Suit.NOTRUMP:
            (bidLevel, bidSuit) = openRsp1NoTrump(hand)

    elif openLevel == 2:
        if openSuit == Suit.CLUB or openSuit == Suit.DIAMOND:
            (bidLevel, bidSuit) = openRsp2Minor(hand, openSuit)
        elif openSuit == Suit.HEART or openSuit == Suit.SPADE:
            (bidLevel, bidSuit) = openRsp2Major(hand, openSuit)
        elif openSuit == Suit.NOTRUMP:
            (bidLevel, bidSuit) = openRsp2NoTrump(hand)

    elif openLevel == 3:
        if openSuit == Suit.CLUB or openSuit == Suit.DIAMOND:
            (bidLevel, bidSuit) = openRsp3Minor(hand, openSuit)
        elif openSuit == Suit.HEART or openSuit == Suit.SPADE:
            (bidLevel, bidSuit) = openRsp3Major(hand, openSuit)
        elif openSuit == Suit.NOTRUMP:
            (bidLevel, bidSuit) = openRsp3NoTrump(hand)

    return (bidLevel, bidSuit)
        

def openRsp1Minor(hand, suit):
    return (1, Suit.HEART)

def openRsp1Major(hand, suit):
    return (2, suit)

def openRsp1NoTrump(hand):
    return (2, Suit.CLUB)

def openRsp2Minor(hand, suit):
    return (2, Suit.HEART)

def openRsp2Major(hand, suit):
    return (3, suit)

def openRsp2NoTrump(hand):
    return (3, Suit.CLUB)

def openRsp3Minor(hand, suit):
    return (3, Suit.HEART)

def openRsp3Major(hand, suit):
    return (4, suit)

def openRsp3NoTrump(hand):
    return (4, Suit.CLUB)
