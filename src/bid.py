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
    if seatNum == 1:
        return True
    else:
        return False

def calcOpenBid(hand):
    return (1, Suit.SPADE)
