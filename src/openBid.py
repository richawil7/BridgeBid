'''
Module for generating an opening bid
'''

from infoLog import Log
from enums import Suit, Level, DistMethod, SuitCategory, Conv
from utils import *
from bidUtils import *
from card import Card
from cardPile import CardPile
from methodRegistry import MethodRegistry
from bidNotif import BidNotif

class OpenerRegistry:
    # Create a registry of functions used by the potential opener
    class OpenerFunctions(MethodRegistry):
        pass

    def __init__(self):
        # Bind methods to instance
        self.jump_table = OpenerRegistry.OpenerFunctions.get_bound_jump_table(self)

    def enforceMinBid(self, table, player, bidLevel, bidSuit):
        # print("enforceMinBid: self is {}".format(self))
        myBidStr = getBidStr(bidLevel, bidSuit)

        # Find the highest bid made at the table so far
        (maxLevel, maxSuit) = findLargestTableBid(table)
        maxBidStr = getBidStr(maxLevel, maxSuit)

        if maxLevel > bidLevel:
            # Competitors already bid higher than my bid. Return pass
            Log.write("enforceMinBid: my bid of %s was squashed by %s\n" % (myBidStr, maxBidStr))
            bidNotif = BidNotif(0, Suit.ALL, player.teamState)
            return bidNotif
        elif maxLevel == bidLevel:
            if maxSuit.value <= bidSuit.value:
                Log.write("enforceMinBid: my bid of %s was squashed by %s\n" % (myBidStr, maxBidStr))
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif

        bidNotif = BidNotif(bidLevel, bidSuit, player.teamState)
        bidNotif.convention = Conv.OPENING
        return bidNotif
        

    # Define functions
    @OpenerFunctions.register(command="open")    
    def calcOpenBid(self, table, player):
        Log.write("calcOpenBid: %s\n" % player.pos.name)
        hand = player.hand
        ts = player.teamState
        (hcPts, lenPts) = hand.evalHand(DistMethod.HCP_LONG)
        totalPts = hcPts + lenPts
        # Find the longest suit
        (numCardsLong, longSuit) = hand.findLongestSuit()
        # Check if we should open weak with a long suit
        if totalPts < 14:
            ts.myMinPoints = 5
            ts.myMaxPoints = 13            
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
            if totalPts != 13 and (not goodMajor):
                # Get the two longest suits
                (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
                # Check for weak bid
                if numCardsLong >= 6:
                    (category, numCardsIHave, highCardCount) = hand.evalSuitCategory(longSuit)
                    if highCardCount >=2:
                        if numCardsB >= 4:
                            bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                            return bidNotif

                        # Weak bid
                        if longSuit != Suit.CLUB:
                            bidLevel = numCardsLong - 4
                            player.playerRole = PlayerRole.OPENER
                            return self.enforceMinBid(table, player, bidLevel, longSuit)
                    else:
                        bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                        return bidNotif
                else:
                    # Check for rule of 20
                    if hcPts + numCardsA + numCardsB >= 20:
                        player.playerRole = PlayerRole.OPENER
                        return self.enforceMinBid(table, player, 1, suitA)
                    else:
                        bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                        return bidNotif
                        return (0, Suit.ALL)

        # Check for balanced hand
        if hand.isHandBalanced():
            if hcPts >= 15 and hcPts <= 17:
                ts.myMinPoints = 15
                ts.myMaxPoints = 17            
                player.playerRole = PlayerRole.OPENER
                return self.enforceMinBid(table, player, 1, Suit.NOTRUMP)
            # Does hand have stoppers in all 4 suits
            if hand.hasStoppers():
                if hcPts >= 18 and hcPts <= 19:
                    ts.myMinPoints = 18
                    ts.myMaxPoints = 19            
                    player.playerRole = PlayerRole.OPENER
                    return self.enforceMinBid(table, player, 1, longSuit)
                if hcPts >= 20 and hcPts <= 21:
                    ts.myMinPoints = 20
                    ts.myMaxPoints = 21            
                    player.playerRole = PlayerRole.OPENER
                    return self.enforceMinBid(table, player, 2, Suit.NOTRUMP)
                if hcPts >= 25 and hcPts <= 27:
                    ts.myMinPoints = 25
                    ts.myMaxPoints = 27            
                    player.playerRole = PlayerRole.OPENER
                    return self.enforceMinBid(table, player, 3, Suit.NOTRUMP)
                if hcPts >= 28 and hcPts <= 29:
                    ts.myMinPoints = 28
                    ts.myMaxPoints = 29            
                    player.playerRole = PlayerRole.OPENER
                    return self.enforceMinBid(table, player, 4, Suit.NOTRUMP)

        # If you get here, the hand is unbalanced or is balanced with 22-24 points
        # Check for a big hand
        if totalPts >= 22:
            ts.myMinPoints = 22
            ts.myMaxPoints = 40            
            player.playerRole = PlayerRole.OPENER
            return self.enforceMinBid(table, player, 2, Suit.CLUB)

        # Check for a long suit
        if numCardsLong >= 5:
            player.playerRole = PlayerRole.OPENER
            return self.enforceMinBid(table, player, 1, longSuit)

        # Bid the longer minor
        longSuit = findLongerMinor(hand)
        player.playerRole = PlayerRole.OPENER
        return self.enforceMinBid(table, player, 1, longSuit)

        print("bid: calcOpenBid: ERROR - did not find bid")        
        print("calcOpenBid: hcPts=%d lenPts=%d suit=%s suitLen=%d" % (hcPts, lenPts, longSuit.name, numCardsLong))

