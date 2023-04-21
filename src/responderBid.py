'''
Functions used for generating bids by the responder after an
opening bid from the partner
'''

from infoLog import Log
from enums import Suit, Level, DistMethod, Conv
from utils import *
from card import Card
from cardPile import CardPile
from methodRegistry import MethodRegistry
from bidUtils import *
from bidNotif import BidNotif

class ResponderRegistry:
    # Create a registry of functions used by the responder
    class ResponderFunctions(MethodRegistry):
        pass

    def __init__(self):
        # Bind methods to instance
        self.jump_table = ResponderRegistry.ResponderFunctions.get_bound_jump_table(self)


    # Define functions
    @ResponderFunctions.register(command="rsp_Pass")
    def openPassRsp(self, table, player):
        Log.write("responderBid: openPassRsp by %s\n" % player.pos.name)
        hand = player.hand
        ts = player.teamState
        (hcPts, lenPts) = hand.evalHand(DistMethod.HCP_LONG)
        totalPts = hcPts + lenPts

        # Find the longest suit
        (numCardsLong, longSuit) = hand.findLongestSuit()
        if totalPts < 14:
            ts.myMinPoints = 0
            ts.myMaxPoints = 13
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
                        return self.enforceMinBid(table, player, bidLevel, longSuit)

            # Check for rule of 20
            if totalPts + numCardsA + numCardsB >= 20:
                return self.enforceMinBid(table, player, 1, suitA)
            else:
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif
                
        # Check for balanced hand
        if hand.isHandBalanced():
            if hcPts >= 15 and hcPts <= 17:
                ts.myMinPoints = 15
                ts.myMaxPoints = 17
                return self.enforceMinBid(table, player, 1, Suit.NOTRUMP)
            # Does hand have stoppers in all 4 suits
            if hand.hasStoppers():
                if hcPts >= 18 and hcPts <= 19:
                    ts.myMinPoints = 18
                    ts.myMaxPoints = 19
                    return self.enforceMinBid(table, player, 1, longSuit)
                if hcPts >= 20 and hcPts <= 21:
                    ts.myMinPoints = 20
                    ts.myMaxPoints = 21
                    return self.enforceMinBid(table, player, 2, Suit.NOTRUMP)
                if hcPts >= 25 and hcPts <= 27:
                    ts.myMinPoints = 25
                    ts.myMaxPoints = 27
                    return self.enforceMinBid(table, player, 3, Suit.NOTRUMP)
                if hcPts >= 28 and hcPts <= 29:
                    ts.myMinPoints = 28
                    ts.myMaxPoints = 29
                    return self.enforceMinBid(table, player, 4, Suit.NOTRUMP)

        # If you get here, the hand is unbalanced or is balanced with 22-24 points
        # Check for a big hand
        if totalPts >= 22:
            ts.myMinPoints = 22
            ts.myMaxPoints = 40
            return self.enforceMinBid(table, player, 2, Suit.CLUB)

        # Check for a long suit
        if numCardsLong >= 5:
            return self.enforceMinBid(table, player, 1, longSuit)

        # Bid the longer minor
        longSuit = findLongerMinor(hand)
        return self.enforceMinBid(table, player, 1, longSuit)

        print("bid: openPassRsp: ERROR - did not find bid")        
        
    
    @ResponderFunctions.register(command="rsp_1Mi")
    def open1MinorRsp(self, table, player):
        Log.write("responderBid: open1MinorRsp by %s\n" % player.pos.name)
        ts = player.teamState
        suit = player.teamState.bidSeq[-1][1]
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        if totalPts < 6:
            ts.myMinPoints = 0
            ts.myMaxPoints = 5
            bidNotif = BidNotif(0, Suit.ALL, player.teamState)
            return bidNotif
        if totalPts < 9 and player.teamState.competition:
            ts.myMinPoints = 6
            ts.myMaxPoints = 8
            bidNotif = BidNotif(0, Suit.ALL, player.teamState)
            return bidNotif

        # Can support opener's suit
        (numBidSuit, numHigh) = player.hand.evalSuitStrength(suit)
        hasSupport = False
        if suit == Suit.DIAMOND and numBidSuit >= 4:
            hasSupport = True
        elif suit == Suit.CLUB and numBidSuit >= 5:
            hasSupport = True
            
        if hasSupport:
            # Can we suggest a major?
            (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
            (numHearts, numHighHearts) = player.hand.evalSuitStrength(Suit.HEART)
            if numSpades >= 4 or numHearts >= 4:
                if numSpades == 5 and numHearts == 5:
                    bidNotif = BidNotif(1, Suit.SPADE, player.teamState)
                    return bidNotif
                elif numSpades == 4 and numHearts == 4:
                    bidNotif = BidNotif(1, Suit.HEART, player.teamState)
                    return bidNotif
                elif numSpades > numHearts:
                    bidNotif = BidNotif(1, Suit.SPADE, player.teamState)
                    return bidNotif
                else:
                    bidNotif = BidNotif(1, Suit.HEART, player.teamState)
                    return bidNotif

            # No 4 card major. Use inverted minors
            if totalPts >=6 and totalPts <= 10:
                ts.myMinPoints = 6
                ts.myMaxPoints = 10
                bidNotif = BidNotif(3, suit, player.teamState)
                return bidNotif
            elif totalPts >=11 and totalPts <= 12:
                ts.myMinPoints = 11
                ts.myMaxPoints = 12
                bidNotif = BidNotif(2, suit, player.teamState)
                return bidNotif
            elif totalPts >=13:
                ts.myMinPoints = 13
                ts.myMaxPoints = 27
                if suit == Suit.DIAMOND:
                    # 2 over 1
                    bidNotif = BidNotif(2, Suit.CLUB, player.teamState)
                    bidNotif.convention = Conv.TWO_OVER_ONE
                    return bidNotif
                else:
                    bidNotif = BidNotif(2, Suit.NOTRUMP, player.teamState)
                    bidNotif.convention = Conv.TWO_OVER_ONE
                    return bidNotif
        else:
            # Can not support opener's minor
            # Can we suggest a major?
            hasMajor = False
            (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
            (numHearts, numHighHearts) = player.hand.evalSuitStrength(Suit.HEART)
            if numSpades >= 4 or numHearts >= 4:
                hasMajor = True

            if totalPts >= 6 and totalPts <= 10:
                ts.myMinPoints = 6
                ts.myMaxPoints = 10
                if suit == Suit.CLUB:
                    (numDiamonds, numHighDiamonds) = player.hand.evalSuitStrength(Suit.DIAMOND)
                    if numDiamonds >= 4:
                        bidNotif = BidNotif(1, Suit.DIAMOND, player.teamState)
                        return bidNotif
                elif hasMajor:
                    if numSpades == 5 and numHearts == 5:
                        bidNotif = BidNotif(1, Suit.SPADE, player.teamState)
                        return bidNotif
                    elif numSpades == 4 and numHearts == 4:
                        bidNotif = BidNotif(1, Suit.HEART, player.teamState)
                        return bidNotif
                    elif numSpades > numHearts:
                        bidNotif = BidNotif(1, Suit.SPADE, player.teamState)
                        return bidNotif
                    else:
                        bidNotif = BidNotif(1, Suit.HEART, player.teamState)
                        return bidNotif
                else:
                    bidNotif = BidNotif(1, Suit.NOTRUMP, player.teamState)
                    return bidNotif

            if totalPts >= 11 and totalPts <= 12:
                ts.myMinPoints = 11
                ts.myMaxPoints = 12
                if hasMajor:
                    if numSpades == 5 and numHearts == 5:
                        bidNotif = BidNotif(1, Suit.SPADE, player.teamState)
                        return bidNotif
                    elif numSpades == 4 and numHearts == 4:
                        bidNotif = BidNotif(1, Suit.HEART, player.teamState)
                        return bidNotif
                    elif numSpades > numHearts:
                        bidNotif = BidNotif(1, Suit.SPADE, player.teamState)
                        return bidNotif
                    else:
                        bidNotif = BidNotif(1, Suit.HEART, player.teamState)
                        return bidNotif
                elif suit == Suit.CLUB:
                    (numDiamonds, numHighDiamonds) = player.hand.evalSuitStrength(Suit.DIAMOND)
                    if numDiamonds >= 4:
                        bidNotif = BidNotif(1, Suit.DIAMOND, player.teamState)
                        return bidNotif
                else:
                    bidNotif = BidNotif(1, Suit.NOTRUMP, player.teamState)
                    return bidNotif

            if totalPts >= 13:
                ts.myMinPoints = 13
                ts.myMaxPoints = 27
                if suit == Suit.DIAMOND:
                    # 2 over 1
                    bidNotif = BidNotif(2, Suit.CLUB, player.teamState)
                    bidNotif.convention = Conv.TWO_OVER_ONE
                    return bidNotif

            if totalPts >= 13 and totalPts <= 15:
                ts.myMinPoints = 13
                ts.myMaxPoints = 15
                if player.hand.isHandBalanced():
                    bidNotif = BidNotif(2, Suit.NOTRUMP, player.teamState)
                    return bidNotif

            if totalPts >= 16 and totalPts <= 18:
                ts.myMinPoints = 16
                ts.myMaxPoints = 18
                if player.hand.isHandBalanced() and player.hand.hasStoppers():
                    bidNotif = BidNotif(3, Suit.NOTRUMP, player.teamState)
                    return bidNotif

            if totalPts >= 13 and hasMajor:
                ts.myMinPoints = 13
                ts.myMaxPoints = 27
                if numSpades == numHearts:
                    bidNotif = BidNotif(1, Suit.HEART, player.teamState)
                    return bidNotif
                elif numSpades > numHearts:
                    bidNotif = BidNotif(1, Suit.SPADE, player.teamState)
                    return bidNotif
                else:
                    bidNotif = BidNotif(1, Suit.HEART, player.teamState)
                    return bidNotif
            else:
                (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
                if suitA != suit:
                    bidNotif = BidNotif(1, suitA, player.teamState)
                    return bidNotif
                else:
                    bidNotif = BidNotif(1, suitB, player.teamState)
                    return bidNotif
                
    @ResponderFunctions.register(command="rsp_1Ma")
    def open1MajorRsp(self, table, player):
        Log.write("responderBid: open1MajorRsp by %s\n" % player.pos.name)
        ts = player.teamState
        suit = player.teamState.bidSeq[-1][1]
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()

        # Can we support the bid suit?
        (numBidSuit, numHigh) = player.hand.evalSuitStrength(suit)
        if numBidSuit >= 3:
            # Can support opener's suit
            singleSuit = player.hand.hasSingletonOrVoid(suit)
            if numBidSuit >= 5 and singleSuit != Suit.ALL:
                bidNotif = BidNotif(4, suit, player.teamState)
                return bidNotif

            if hcPts < 6:
                ts.myMinPoints = 0
                ts.myMaxPoints = 5
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif
            if hcPts < 9 and player.teamState.competition:
                ts.myMinPoints = 6
                ts.myMaxPoints = 8
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif

            if totalPts >= 6 and totalPts <= 10:
                ts.myMinPoints = 6
                ts.myMaxPoints = 10
                bidNotif = BidNotif(2, suit, player.teamState)
                return bidNotif

            if totalPts >= 11 and totalPts <= 12:
                # Major limit raise
                ts.myMinPoints = 11
                ts.myMaxPoints = 12
                bidNotif = BidNotif(3, suit, player.teamState)
                return bidNotif

            if totalPts >= 13:
                ts.myMinPoints = 13
                ts.myMaxPoints = 27
                if numBidSuit >= 4:
                    if singleSuit != Suit.ALL:
                        # Splinter
                        bidNotif = BidNotif(4, singleSuit, player.teamState)
                        bidNotif.convention = Conv.SPLINTER
                        return bidNotif
                    elif player.hand.isHandBalanced():
                        # Jacoby 2NT
                        bidNotif = BidNotif(2, Suit.NOTRUMP, player.teamState)
                        bidNotif.convention = Conv.JACOBY_2NT             
                        return bidNotif
                else:
                    # 2 over 1
                    if suitA.value < suit.value:
                        bidNotif = BidNotif(2, suitA, player.teamState)
                        bidNotif.convention = Conv.TWO_OVER_ONE
                        return bidNotif
                    if suitB.value < suit.value:
                        bidNotif = BidNotif(2, suitB, player.teamState)
                        bidNotif.convention = Conv.TWO_OVER_ONE
                        return bidNotif
                    bidNotif = BidNotif(2, Suit.CLUB, player.teamState)
                    bidNotif.convention = Conv.TWO_OVER_ONE
                    return bidNotif
        else:
            # Do not have support for opener's major
            if hcPts < 6:
                ts.myMinPoints = 5
                ts.myMaxPoints = 5
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif
            if hcPts < 9 and player.teamState.competition:
                ts.myMinPoints = 6
                ts.myMaxPoints = 8
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif

            if totalPts >= 6 and totalPts <= 12:
                ts.myMinPoints = 6
                ts.myMaxPoints = 12
                if suit == Suit.HEART:
                    (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
                    if numSpades >= 4:
                        bidNotif = BidNotif(1, Suit.SPADE, player.teamState)
                        return bidNotif
                bidNotif = BidNotif(1, Suit.NOTRUMP, player.teamState)
                return bidNotif

            if totalPts >= 13:
                ts.myMinPoints = 13
                ts.myMaxPoints = 27                
                # Can we bid 2 over 1? Need a long suit less than the bid suit
                if suitA.value > suit.value:
                    bidNotif = BidNotif(2, suitA, player.teamState)
                    bidNotif.convention = Conv.TWO_OVER_ONE
                    return bidNotif
                if suitB.value > suit.value:
                    bidNotif = BidNotif(2, suitB, player.teamState)
                    bidNotif.convention = Conv.TWO_OVER_ONE
                    return bidNotif
                
                if player.hand.isHandBalanced():
                    if totalPts >= 13 and totalPts <= 15:
                        ts.myMinPoints = 13
                        ts.myMaxPoints = 15
                        bidNotif = BidNotif(2, Suit.NOTRUMP, player.teamState)
                        return bidNotif
                    if totalPts >= 16 and totalPts <= 18:
                        ts.myMinPoints = 16
                        ts.myMaxPoints = 18
                        bidNotif = BidNotif(3, Suit.NOTRUMP, player.teamState)
                        return bidNotif

                # Just bid best suit up the line
                if numCardsA > numCardsB:
                    bidNotif = BidNotif(1, suitA, player.teamState)
                    return bidNotif
                elif numCardsB > numCardsA:
                    bidNotif = BidNotif(1, suitB, player.teamState)
                    return bidNotif
                else:
                    if suitA.value > suitB.value:
                        bidNotif = BidNotif(1, suitA, player.teamState)
                        return bidNotif
                    else:
                        bidNotif = BidNotif(1, suitB, player.teamState)
                        return bidNotif
                        

    @ResponderFunctions.register(command="rsp_1NT")    
    def open1NoTrumpRsp(self, table, player):
        Log.write("responderBid: open1NoTrumpRsp by %s\n" % player.pos.name)
        ts = player.teamState
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        # Do I have a 6+ card major?
        (numHearts, numHighHearts) = player.hand.evalSuitStrength(Suit.HEART)
        (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
        if numHearts >= numSpades:
            suitA = Suit.HEART
        else:
            suitA = Suit.SPADE
            
        if numSpades >= 6 or numHearts >= 6:
            if hcPts >= 10 and hcPts <= 15:
                ts.myMinPoints = 10
                ts.myMaxPoints = 15
                if numHearts >= numSpades:
                    bidNotif = BidNotif(4, Suit.HEART, player.teamState)
                else:
                    bidNotif = BidNotif(4, Suit.SPADE, player.teamState)
                return bidNotif

        # Do I have a 6+ card minor?
        (numDiamonds, numHighDiamonds) = player.hand.evalSuitStrength(Suit.DIAMOND)
        (numClubs, numHighClubs) = player.hand.evalSuitStrength(Suit.CLUB)
        if numDiamonds >= 6 or numClubs >= 6:
            if hcPts >= 8:
                ts.myMinPoints = 8
                ts.myMaxPoints = 27
                bidNotif = BidNotif(3, Suit.NOTRUMP, player.teamState)
                return bidNotif

        # Do I have a 5+ card major
        if numSpades >= 5 or numHearts >= 5:
            if hcPts < 8:
                ts.myMinPoints = 0
                ts.myMaxPoints = 7
                # Jacoby transfer
                if suitA == Suit.HEART:
                    bidNotif = BidNotif(2, Suit.DIAMOND, player.teamState)
                else:
                    bidNotif = BidNotif(2, Suit.HEART, player.teamState)
                bidNotif.convention = Conv.JACOBY_XFER_REQ
                return bidNotif
            elif hcPts >= 8 and hcPts <= 9:
                ts.myMinPoints = 8
                ts.myMaxPoints = 9
                # Stayman
                bidNotif = BidNotif(2, Suit.CLUB, player.teamState)
                bidNotif.convention = Conv.STAYMAN_REQ
                return bidNotif
            elif hcPts >= 10:
                ts.myMinPoints = 10
                ts.myMaxPoints = 25
                # Jacoby transfer
                if suitA == Suit.HEART:
                    bidNotif = BidNotif(2, Suit.DIAMOND, player.teamState)
                else:
                    bidNotif = BidNotif(2, Suit.HEART, player.teamState)
                bidNotif.convention = Conv.JACOBY_XFER_REQ
                return bidNotif

        # Do I have a 4+ card major
        if numSpades >= 4 or numHearts >= 4:
            if hcPts >= 8:
                ts.myMinPoints = 8
                ts.myMaxPoints = 25
                # Stayman
                bidNotif = BidNotif(2, Suit.CLUB, player.teamState)
                bidNotif.convention = Conv.STAYMAN_REQ
                return bidNotif

        # If I get here, we don't have a 4+ card major
        if numClubs >= 5:
            bidNotif = BidNotif(2, Suit.SPADE, player.teamState)
            bidNotif.convention = Conv.JACOBY_XFER_REQ
            return bidNotif

        # Natural bid from here on out
        balancedHand = player.hand.isHandBalanced()
        if balancedHand:
            if hcPts <= 7:
                ts.myMinPoints = 0
                ts.myMaxPoints = 7
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif
            if hcPts >= 8 and hcPts <= 9:
                ts.myMinPoints = 8
                ts.myMaxPoints = 9
                bidNotif = BidNotif(2, Suit.NOTRUMP, player.teamState)
                return bidNotif
            elif hcPts >= 10 and hcPts <= 15:
                ts.myMinPoints = 10
                ts.myMaxPoints = 15
                bidNotif = BidNotif(3, Suit.NOTRUMP, player.teamState)
                return bidNotif
            elif hcPts >= 16 and hcPts <= 17:
                ts.myMinPoints = 16
                ts.myMaxPoints = 17
                bidNotif = BidNotif(4, Suit.NOTRUMP, player.teamState)
                return bidNotif
            elif hcPts >= 18 and hcPts <= 19:
                ts.myMinPoints = 18
                ts.myMaxPoints = 19
                bidNotif = BidNotif(6, Suit.NOTRUMP, player.teamState)
                return bidNotif
            elif hcPts >= 20 and hcPts <= 21:
                ts.myMinPoints = 20
                ts.myMaxPoints = 21
                bidNotif = BidNotif(5, Suit.NOTRUMP, player.teamState)
                return bidNotif
            elif hcPts >= 22:
                ts.myMinPoints = 22
                ts.myMaxPoints = 27
                bidNotif = BidNotif(7, Suit.NOTRUMP, player.teamState)
                return bidNotif
            
        # Not a balanced hand    
        if hcPts <= 7:
            ts.myMinPoints = 0
            ts.myMaxPoints = 7
            bidNotif = BidNotif(0, Suit.ALL, player.teamState)
            return bidNotif

    @ResponderFunctions.register(command="rsp_2C")
    def open2ClubRsp(self, table, player):
        Log.write("responderBid: open2ClubRsp by %s\n" % player.pos.name)
        ts = player.teamState
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        if hcPts < 8:
            ts.myMinPoints = 0
            ts.myMaxPoints = 7
            bidNotif = BidNotif(2, Suit.DIAMOND, player.teamState)
            return bidNotif

        ts.myMinPoints = 8
        ts.myMaxPoints = 18
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if numCardsA >= 5:
            if suitA == Suit.DIAMOND:
                bidNotif = BidNotif(3, suitA, player.teamState)
                return bidNotif
            else:
                bidNotif = BidNotif(2, suitA, player.teamState)
                return bidNotif

        balancedHand = player.hand.isHandBalanced()
        if balancedHand:
            bidNotif = BidNotif(2, Suit.NOTRUMP, player.teamState)
            return bidNotif

        bidNotif = BidNotif(2, Suit.DIAMOND, player.teamState)
        return bidNotif


    @ResponderFunctions.register(command="rsp_2Weak") 
    def openWeakRsp(self, table, player):
        Log.write("responderBid: openWeakRsp by %s\n" % player.pos.name)
        ts = player.teamState
        # Get the bid from my partner
        level = player.teamState.bidSeq[-1][0]
        suit = player.teamState.bidSeq[-1][1]
        
        # How many points do I have?
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        (category, numCardsIHave, highCardCount) = player.hand.evalSuitCategory(suit)
        numCardsWeHave = numCardsIHave + level + 4

        # Handle the case where we have a fit
        if numCardsWeHave >= 8:
            if hcPts >= 14:
                ts.myMinPoints = 14
                ts.myMaxPoints = 35
                bidNotif = BidNotif(2, Suit.NOTRUMP, player.teamState)
                return bidNotif
                
            if totalPts >= 8 and totalPts <= 13:
                ts.myMinPoints = 8
                ts.myMaxPoints = 13
                # Bid 4                
                if level < 4:
                    bidNotif = BidNotif(4, suit, player.teamState)
                    return bidNotif
                else:
                    bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                    return bidNotif
            
            ts.myMinPoints = 0
            ts.myMaxPoints = 7
            if numCardsWeHave == 8:
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif
            elif numCardsWeHave == 9:
                if level < 3:
                    bidNotif = BidNotif(3, suit, player.teamState)
                    return bidNotif
                else:
                    bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                    return bidNotif
            elif numCardsWeHave >= 10:
                if level < 4:
                    bidNotif = BidNotif(4, suit, player.teamState)
                    return bidNotif
                else:
                    bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                    return bidNotif
        else:
            # We don't have a fit. Pass if opened above the 2 level
            if level >= 3:
                ts.myMinPoints = 0
                ts.myMaxPoints = 21
                bidNotif = BidNotif(0, Suit.ALL, player.teamState)
                return bidNotif

            # I can show a new 6 card suit           
            ts.myMinPoints = 0
            ts.myMaxPoints = 13
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if numCardsA >= 6 and suitA.value > suit.value:
                bidNotif = BidNotif(level, suitA, player.teamState)
                return bidNotif
            if numCardsB >= 6 and suitB.value > suit.value:
                bidNotif = BidNotif(level, suitB, player.teamState)
                return bidNotif
            if numCardsA >= 6 and suitA > Suit.CLUB:
                bidNotif = BidNotif(3, Suit.CLUB, player.teamState)
                return bidNotif
            
            if player.hand.hasStoppers():
                numCardsOppHas = 13 - numCardsWeHave
                if highCardCount * 2 >= numCardOppHave:
                    bidNotif = BidNotif(3, Suit.NOTRUMP, player.teamState)
                    return bidNotif

            # Can we bid a 5 card suit at the 2 level
            if hcPts >= 15 and numCardsA >= 5 and suitA.value < suit.value and level == 2:
                bidNotif = BidNotif(2, suitA, player.teamState)
                return bidNotif

            # Check if we should commit a sacrifice
            # Sacrifice if you will go down by no more than 2 tricks
            minTricks = 6 + level + 1 - 2
            # HACK: use a vastly simplified estimate of number of tricks we will take
            winTricks = 4 + int((totalPts + 8)/5)
            if winTricks >= minTricks:
                bidNotif = BidNotif(level+1, bidSuit, player.teamState)
                return bidNotif

        bidNotif = BidNotif(0, Suit.ALL, player.teamState)
        return bidNotif


    @ResponderFunctions.register(command="rsp_2NT")    
    def open2NoTrumpRsp(self, table, player):
        Log.write("responderBid: open2NoTrumpRsp by %s\n" % player.pos.name)
        ts = player.teamState
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        # Do I have a 6+ card major?
        (numHearts, numHighHearts) = player.hand.evalSuitStrength(Suit.HEART)
        (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
        if numHearts >= numSpades:
            suitA = Suit.HEART
        else:
            suitA = Suit.SPADE
            
        if numSpades >= 5 or numHearts >= 5:
            ts.myMinPoints = 0
            ts.myMaxPoints = 20
            # Jacoby transfer
            if suitA == Suit.HEART:
                bidNotif = BidNotif(2, Suit.DIAMOND, player.teamState)
            else:
                bidNotif = BidNotif(2, Suit.HEART, player.teamState)
            bidNotif.convention = Conv.JACOBY_XFER_REQ
            return bidNotif

        # Do I have a 4+ card major
        if numSpades >= 4 or numHearts >= 4:
            if hcPts >= 6:
                ts.myMinPoints = 6
                ts.myMaxPoints = 20
                # Stayman
                bidNotif = BidNotif(2, Suit.CLUB, player.teamState)
                bidNotif.convention = Conv.STAYMAN_REQ
                return bidNotif

        (numClubs, numHighClubs) = player.hand.evalSuitStrength(Suit.CLUB)
        if numClubs >= 5:
            ts.myMinPoints = 0
            ts.myMaxPoints = 20
            # Jacoby transfer
            bidNotif = BidNotif(2, Suit.SPADE, player.teamState)
            bidNotif.convention = Conv.JACOBY_XFER_REQ
            return bidNotif

        # No 4 card major or 5 clubs
        if hcPts < 5:
            ts.myMinPoints = 0
            ts.myMaxPoints = 4
            bidNotif = BidNotif(0, Suit.ALL, player.teamState)
            return bidNotif
        if hcPts >= 5 and hcPts <= 11:
            ts.myMinPoints = 5
            ts.myMaxPoints = 11
            bidNotif = BidNotif(3, Suit.NOTRUMP, player.teamState)
            return bidNotif
        if hcPts == 12:
            ts.myMinPoints = 12
            ts.myMaxPoints = 12
            bidNotif = BidNotif(4, Suit.NOTRUMP, player.teamState)
            return bidNotif
        if hcPts >= 13 and hcPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15
            bidNotif = BidNotif(6, Suit.NOTRUMP, player.teamState)
            return bidNotif
        if hcPts == 16:
            ts.myMinPoints = 16
            ts.myMaxPoints = 16
            bidNotif = BidNotif(5, Suit.NOTRUMP, player.teamState)
            return bidNotif
        if hcPts >= 17:
            ts.myMinPoints = 17
            ts.myMaxPoints = 20
            bidNotif = BidNotif(7, Suit.NOTRUMP, player.teamState)
            return bidNotif

    @ResponderFunctions.register(command="rsp_3NT")    
    def open3NoTrumpRsp(self, table, player):
        Log.write("responderBid: open3NoTrumpRsp by %s\n" % player.pos.name)
        ts = player.teamState
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        if hcPts == 7:
            ts.myMinPoints = 7
            ts.myMaxPoints = 7
            bidNotif = BidNotif(4, Suit.NOTRUMP, player.teamState)
            return bidNotif
        if hcPts >= 8 and hcPts <= 9:
            ts.myMinPoints = 8
            ts.myMaxPoints = 9
            bidNotif = BidNotif(6, Suit.NOTRUMP, player.teamState)
            return bidNotif
        if hcPts >= 10 and hcPts <= 11:
            ts.myMinPoints = 10
            ts.myMaxPoints = 11
            bidNotif = BidNotif(5, Suit.NOTRUMP, player.teamState)
            return bidNotif
        if hcPts >= 12:
            ts.myMinPoints = 12
            ts.myMaxPoints = 20
            bidNotif = BidNotif(7, Suit.NOTRUMP, player.teamState)
            return bidNotif
