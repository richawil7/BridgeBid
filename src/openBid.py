'''
Module for generating an opening bid
'''

from enums import Suit, Level, DistMethod, SuitCategory
from utils import *
from bidUtils import *
from card import Card
from cardPile import CardPile
from methodRegistry import MethodRegistry


class OpenerRegistry:
    # Create a registry of functions used by the potential opener
    class OpenerFunctions(MethodRegistry):
        pass

    def __init__(self):
        # Bind methods to instance
        self.jump_table = OpenerRegistry.OpenerFunctions.get_bound_jump_table(self)

    def checkCompetition(self, table, bidLevel, bidSuit):
        myBidStr = getBidStr(bidLevel, bidSuit)
        print("checkCompetition: for bid %s" % myBidStr)
        # Check if there is competition
        if not table.competition:
            return (bidLevel, bidSuit)
        
        # Find the competitor's bid
        numBids = len(table.bidsList)
        minBid = table.bidsList[-1]
        if numBids == 3 and minBid[0] == 0:
            minBid = table.bidsList[-3]

        bidStr = getBidStr(minBid[0], minBid[1])
        print("checkCompetition: competition bid" % bidStr)
            
        if minBid[0] > bidLevel:
            # Competitors already bid higher than my bid. Return pass
            print("checkCompetition: my bid of %s was squashed" % myBidStr)
            return (0, Suit.ALL)
        if minBid[1].level >= bidSuit.level:
            print("checkCompetition: my bid of %s was squashed" % myBidStr)
            return (0, Suit.ALL)

        return (bidLevel, bidSuit)
        

    # Define functions
    @OpenerFunctions.register(command="open")    
    def calcOpenBid(self, table, player):
        print("openBid: calcOpenBid: entry")
        hand = player.hand
        (hcPts, lenPts) = hand.evalHand(DistMethod.HCP_LONG)
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
                # Get the two longest suits
                (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
                # Check for weak bid
                if numCardsLong >= 6:
                    (category, numCardsIHave, highCardCount) = hand.evalSuitCategory(longSuit)
                    if highCardCount >=2:
                        if numCardsB >= 4:
                            return (0, Suit.ALL)

                        # Weak bid
                        if longSuit != Suit.CLUB:
                            bidLevel = numCardsLong - 4
                            return self.checkCompetition(table, bidLevel, longSuit)
                else:
                    # Check for rule of 20
                    if totalPts + numCardsA + numCardsB >= 20:
                        return self.checkCompetition(table, 1, suitA)

        # Check for balanced hand
        if hand.isHandBalanced():
            if hcPts >= 15 and hcPts <= 17:
                return self.checkCompetition(table, 1, Suit.NOTRUMP)
            # Does hand have stoppers in all 4 suits
            if hand.hasStoppers():
                if hcPts >= 18 and hcPts <= 19:
                    return self.checkCompetition(table, 1, longSuit)
                if hcPts >= 20 and hcPts <= 21:
                    return self.checkCompetition(table, 2, Suit.NOTRUMP)
                if hcPts >= 25 and hcPts <= 27:
                    return self.checkCompetition(table, 3, Suit.NOTRUMP)
                if hcPts >= 28 and hcPts <= 29:
                    return self.checkCompetition(table, 4, Suit.NOTRUMP)

        # If you get here, the hand is unbalanced or is balanced with 22-24 points
        # Check for a big hand
        if totalPts >= 22:
            return self.checkCompetition(table, 2, Suit.CLUB)

        # Check for a long suit
        if numCardsLong >= 5:
            return self.checkCompetition(table, 1, longSuit)

        # Bid the longer minor
        longSuit = findLongerMinor(hand)
        return self.checkCompetition(table, 1, longSuit)

        print("bid: calcOpenBid: ERROR - did not find bid")        
        print("calcOpenBid: hcPts=%d lenPts=%d suit=%s suitLen=%d" % (hcPts, lenPts, longSuit.name, numCardsLong))

