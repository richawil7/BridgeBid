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

    # Define functions
    @OpenerFunctions.register(command="open")    
    def calcOpenBid(self, table, player):
        Log.write("calcOpenBid: %s\n" % player.pos.name)
        hand = player.hand
        ts = player.teamState
        (hcPts, lenPts) = hand.evalHand(DistMethod.HCP_LONG)
        totalPts = hcPts + lenPts
        
        # Let's look for a suit to bid
        proposedSuit = Suit.ALL
        (numCardsLong, longSuit) = hand.findLongestSuit()
        (clubCat, numClubs, numClubHc) = hand.evalSuitCategory(Suit.CLUB)
        (diamondCat, numDiamonds, numDiamondHc) = hand.evalSuitCategory(Suit.DIAMOND)
        (heartCat, numHearts, numHeartHc) = hand.evalSuitCategory(Suit.HEART)
        (spadeCat, numSpades, numSpadeHc) = hand.evalSuitCategory(Suit.SPADE)
        if numHearts >= 5 or numSpades >= 5:
            if numHearts == numSpades:
                proposedSuit = Suit.SPADE
            else:
                proposedSuit = Suit.HEART
        elif numDiamonds >= 4:
            proposedSuit = Suit.DIAMOND
        elif numClubs >= 3:
            proposedSuit = Suit.CLUB
        elif numDiamonds >= numClubs:
            proposedSuit = Suit.DIAMOND
        else:
            proposedSuit = Suit.CLUB 
       
        # Now look at my hand's total points    
        # Do I have exactly 13 points
        if totalPts == 13:
            ts.myMinPoints = 13
            ts.myMaxPoints = 21
            # Do I have a good 5+ card major
            if numHearts >= 5 or numSpades >= 5:
                if numHearts >= numSpades:
                    bidNotif = BidNotif(player, 1, Suit.HEART)
                    return bidNotif
                else:
                    bidNotif = BidNotif(player, 1, Suit.SPADE)
                    return bidNotif
            
            # Do I have good hearts?
            if numHearts >= 4 and numHeartHc >= 2:
                if heartCat == SuitCategory.AKQ or \
                   heartCat == SuitCategory.AKx or \
                   heartCat == SuitCategory.AxQ or \
                   heartCat == SuitCategory.xKQ or \
                   heartCat == SuitCategory.Axx:
                    bidNotif = BidNotif(player, 1, Suit.HEART)
                    return bidNotif

            # Do I have good spades?
            if numHearts >= 4 and numSpadeHc >= 2:
                if spadeCat == SuitCategory.AKQ or \
                   spadeCat == SuitCategory.AKx or \
                   spadeCat == SuitCategory.AxQ or \
                   spadeCat == SuitCategory.xKQ or \
                   spadeCat == SuitCategory.Axx:
                    bidNotif = BidNotif(player, 1, Suit.HEART)
                    return bidNotif

            # Do I have 2 quick tricks in clubs?
            if numClubs >= 3:
                if clubCat == SuitCategory.AKQ or \
                   clubCat == SuitCategory.AKx or \
                   clubCat == SuitCategory.AxQ or \
                   clubCat == SuitCategory.xKQ:
                    bidNotif = BidNotif(player, 1, Suit.CLUB)
                    return bidNotif

            # Do I have 2 quick tricks in diamonds?
            if numDiamonds >= 4:
                if diamondCat == SuitCategory.AKQ or \
                   diamondCat == SuitCategory.AKx or \
                   diamondCat == SuitCategory.AxQ or \
                   diamondCat == SuitCategory.xKQ:
                    bidNotif = BidNotif(player, 1, Suit.DIAMOND)
                    return bidNotif
                
        # Check if we should open weak with a long suit
        if totalPts < 14:
            ts.myMinPoints = 5
            ts.myMaxPoints = 13            
            # Get the two longest suits
            (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
            # Check for weak bid
            if numCardsLong >= 6:
                (category, numCardsIHave, highCardCount) = hand.evalSuitCategory(longSuit)
                if highCardCount >=2:
                    if numCardsB >= 4:
                        bidNotif = BidNotif(player, 0, Suit.ALL)
                        return bidNotif

                    # Weak bid
                    if longSuit != Suit.CLUB:
                        bidLevel = numCardsLong - 4
                        player.playerRole = PlayerRole.OPENER
                        return BidNotif(player, bidLevel, longSuit, Conv.OPENING)
                else:
                    bidNotif = BidNotif(player, 0, Suit.ALL)
                    return bidNotif
            else:
                # Check for rule of 20
                if hcPts + numCardsA + numCardsB >= 20:
                    player.playerRole = PlayerRole.OPENER
                    bidNotif = BidNotif(player, 1, proposedSuit, Conv.OPENING)
                else:
                    bidNotif = BidNotif(player, 0, Suit.ALL, Conv.OPENING)
                return bidNotif
            bidNotif = BidNotif(player, 0, Suit.ALL)
            return bidNotif

        # Check for balanced hand
        if hand.isHandBalanced():
            if hcPts >= 15 and hcPts <= 17:
                ts.myMinPoints = 15
                ts.myMaxPoints = 17            
                player.playerRole = PlayerRole.OPENER
                return BidNotif(player, 1, Suit.NOTRUMP, Conv.OPENING)
            # Does hand have stoppers in all 4 suits
            if hand.hasStoppers():
                if hcPts >= 18 and hcPts <= 19:
                    ts.myMinPoints = 18
                    ts.myMaxPoints = 19            
                    player.playerRole = PlayerRole.OPENER
                    return BidNotif(player, 1, longSuit, Conv.OPENING)
                if hcPts >= 20 and hcPts <= 21:
                    ts.myMinPoints = 20
                    ts.myMaxPoints = 21            
                    player.playerRole = PlayerRole.OPENER
                    return BidNotif(player, 2, Suit.NOTRUMP, Conv.OPENING)
                if hcPts >= 25 and hcPts <= 27:
                    ts.myMinPoints = 25
                    ts.myMaxPoints = 27            
                    player.playerRole = PlayerRole.OPENER
                    return BidNotif(player, 3, Suit.NOTRUMP, Conv.OPENING)
                if hcPts >= 28 and hcPts <= 29:
                    ts.myMinPoints = 28
                    ts.myMaxPoints = 29            
                    player.playerRole = PlayerRole.OPENER
                    return BidNotif(player, 4, Suit.NOTRUMP, Conv.OPENING)

        # If you get here, the hand is unbalanced or is balanced with 22-24 points
        # Check for a big hand
        if totalPts >= 22:
            ts.myMinPoints = 22
            ts.myMaxPoints = 40            
            player.playerRole = PlayerRole.OPENER
            return BidNotif(player, 2, Suit.CLUB, Conv.OPENING)

        # Check for a long suit
        if numCardsLong >= 5:
            player.playerRole = PlayerRole.OPENER
            return BidNotif(player, 1, longSuit, Conv.OPENING)

        # Bid the longer minor
        longSuit = findLongerMinor(hand)
        player.playerRole = PlayerRole.OPENER
        return BidNotif(player, 1, longSuit, Conv.OPENING)

        print("bid: calcOpenBid: ERROR - did not find bid")        
        print("calcOpenBid: hcPts=%d lenPts=%d suit=%s suitLen=%d" % (hcPts, lenPts, longSuit.name, numCardsLong))

