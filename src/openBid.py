'''
Functions used for generating bids
'''

from enums import Suit, Level, DistMethod, SuitCategory
from utils import *
from bidUtils import *
from card import Card
from cardPile import CardPile
    
def calcOpenBid(hand):
    (hcPts, lenPts) = hand.evalHand(DistMethod.LONG)
    totalPts = hcPts + lenPts

    # Find the longest suit
    (numCardsLong, longSuit) = hand.findLongestSuit()
    
    # Check if we should open weak with a long suit
    if totalPts < 14:
        # Evaluate spades
        (spadeCat, numSpades, numSpadeHc) = hand.evalSuitCategory(Suit.SPADE)
        # Do we have 2 quick tricks?
        if spadeCat == SuitCategory.AKQ or \
           spadeCat == SuitCategory.AKx or \
           (spadeCat == SuitCategory.AxQ and numSpades > 2) or \
           (spadeCat == SuitCategory.xKQ and numSpades > 2):
            quick2Spades = True
        else:
            quick2Spades = False
        goodSpades = numSpades >= 4 and quick2Spades
        
        # Evaluate hearts
        (heartCat, numHearts, numHeartHc) = hand.evalSuitCategory(Suit.HEART)
        # Do we have 2 quick tricks?
        if heartCat == SuitCategory.AKQ or \
           heartCat == SuitCategory.AKx or \
           (heartCat == SuitCategory.AxQ and numHearts > 2) or \
           (heartCat == SuitCategory.xKQ and numHearts > 2):
            quick2Hearts = True
        else:
            quick2Hearts = False
        goodHearts = numHearts >= 4 and quick2Hearts
        
        goodMajor = goodSpades or goodHearts
        if totalPts != 13 or (not goodMajor):
            # Check for weak bid
            if numCardsLong >= 6:
                (category, numCardsIHave, highCardCount) = hand.evalSuitCategory(longSuit)
                if highCardCount >=2:
                    (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
                    if numCardsB >= 4:
                        return (0, Suit.ALL)

                    # Weak bid
                    if longSuit != Suit.CLUB:
                        bidLevel = numCardsLong - 4
                        return (bidLevel, longSuit)
            return (0, Suit.ALL)
        
    # Check for balanced hand
    if hand.isHandBalanced():
        if hcPts >= 15 and hcPts <= 17:
            return (1, Suit.NOTRUMP)
        # Does hand have stoppers in all 4 suits
        if hand.hasStoppers():
            if hcPts >= 18 and hcPts <= 19:
                return (1, longSuit)
            if hcPts >= 20 and hcPts <= 21:
                return (2, Suit.NOTRUMP)
            if hcPts >= 25 and hcPts <= 27:
                return (3, Suit.NOTRUMP)
            if hcPts >= 28 and hcPts <= 29:
                return (4, Suit.NOTRUMP)

    # If you get here, the hand is unbalanced or is balanced with 22-24 points
    # Check for a big hand
    if totalPts >= 22:
        return (2, Suit.CLUB)
    
    # Check for a long suit
    if numCardsLong >= 5:
        return (1, longSuit)
    
    # Bid the longer minor
    longSuit = findLongerMinor(hand)
    return (1, longSuit)
    
    print("bid: calcOpenBid: did not find bid")        
    print("calcOpenBid: hcPts=%d lenPts=%d suit=%s suitLen=%d" % (hcPts, lenPts, longSuit.name, numCardsLong))
            
