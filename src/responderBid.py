'''
Functions used for generating bids by the responder after an
opening bid from the partner
'''

from enums import Suit, Level, DistMethod
from utils import *
from card import Card
from cardPile import CardPile
from methodRegistry import MethodRegistry


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
        writeLog(table, "responderBid: openPassRsp by %s\n" % player.pos.name)
        hand = player.hand
        (hcPts, lenPts) = hand.evalHand(DistMethod.HCP_LONG)
        totalPts = hcPts + lenPts

        # Find the longest suit
        (numCardsLong, longSuit) = hand.findLongestSuit()
        
        if totalPts < 14:
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

                # Check for rule of 20
                if totalPts + numCardsA + numCardsB >= 20:
                    return self.checkCompetition(table, 1, suitA)
                else:
                    return (0, Suit.ALL)
                
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

        print("bid: openPassRsp: ERROR - did not find bid")        
        print("openPassRsp: hcPts=%d lenPts=%d suit=%s suitLen=%d" % (hcPts, lenPts, longSuit.name, numCardsLong))
        
    
    @ResponderFunctions.register(command="rsp_1Mi")
    def open1MinorRsp(self, table, player):
        writeLog(table, "responderBid: open1MinorRsp by %s\n" % player.pos.name)
        suit = player.teamState.bidSeq[-1][1]
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        if totalPts < 6:
            return (0, Suit.ALL)
        if totalPts < 9 and table.competition:
            return (0, Suit.ALL)

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
                    return (1, Suit.SPADE)
                elif numSpades == 4 and numHearts == 4:
                    return (1, Suit.HEART)
                elif numSpades > numHearts:
                    return (1, Suit.SPADE)
                else:
                    return (1, Suit.HEART)

            # No 4 card major. Use inverted minors
            if totalPts >=6 and totalPts <= 10:
                return (3, suit)
            elif totalPts >=11 and totalPts <= 12:
                return (2, suit)
            elif totalPts >=13:
                if suit == Suit.DIAMOND:
                    # 2 over 1
                    return (2, Suit.CLUB)
                else:
                    return (2, Suit.NOTRUMP)
        else:
            # Can not support opener's minor
            # Can we suggest a major?
            hasMajor = False
            (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
            (numHearts, numHighHearts) = player.hand.evalSuitStrength(Suit.HEART)
            if numSpades >= 4 or numHearts >= 4:
                hasMajor = True

            if totalPts >= 6 and totalPts <= 10:
                if suit == Suit.CLUB:
                    (numDiamonds, numHighDiamonds) = player.hand.evalSuitStrength(Suit.DIAMOND)
                    if numDiamonds >= 4:
                        return (1, Suit.DIAMOND)
                elif hasMajor:
                    if numSpades == 5 and numHearts == 5:
                        return (1, Suit.SPADE)
                    elif numSpades == 4 and numHearts == 4:
                        return (1, Suit.HEART)
                    elif numSpades > numHearts:
                        return (1, Suit.SPADE)
                    else:
                        return (1, Suit.HEART)
                else:
                    return (1, Suit.NOTRUMP)

            if totalPts >= 11 and totalPts <= 12:
                if hasMajor:
                    if numSpades == 5 and numHearts == 5:
                        return (1, Suit.SPADE)
                    elif numSpades == 4 and numHearts == 4:
                        return (1, Suit.HEART)
                    elif numSpades > numHearts:
                        return (1, Suit.SPADE)
                    else:
                        return (1, Suit.HEART)
                elif suit == Suit.CLUB:
                    (numDiamonds, numHighDiamonds) = player.hand.evalSuitStrength(Suit.DIAMOND)
                    if numDiamonds >= 4:
                        return (1, Suit.DIAMOND)
                else:
                    return (1, Suit.NOTRUMP)

            if totalPts >= 13:
                if suit == Suit.DIAMOND:
                    # 2 over 1
                    return (2, Suit.CLUB)

            if totalPts >= 13 and totalPts <= 15:
                if player.hand.isHandBalanced():
                    return (2, Suit.NOTRUMP)

            if totalPts >= 16 and totalPts <= 18:
                if player.hand.isHandBalanced() and player.hand.hasStoppers():
                    return (3, Suit.NOTRUMP)

            if totalPts >= 13 and hasMajor:
                if numSpades == numHearts:
                    return (1, Suit.HEART)
                elif numSpades > numHearts:
                    return (1, Suit.SPADE)
                else:
                    return (1, Suit.HEART)
            else:
                (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
                if suitA != suit:
                    return (1, suitA)
                else:
                    return (1, suitB)

                
    @ResponderFunctions.register(command="rsp_1Ma")
    def open1MajorRsp(self, table, player):
        writeLog(table, "responderBid: open1MajorRsp by %s\n" % player.pos.name)
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
                return (4, suit)

            if hcPts < 6:
                return (0, Suit.ALL)
            if hcPts < 9 and table.competition:
                return (0, Suit.ALL)

            if totalPts >= 6 and totalPts <= 10:
                return (2, suit)

            if totalPts >= 11 and totalPts <= 12:
                # Major limit raise
                return (3, suit)

            if totalPts >= 13:
                if numBidSuit >= 4:
                    if singleSuit != Suit.ALL:
                        # Splinter
                        return (4, singleSuit)
                    elif player.hand.isHandBalanced():
                        # Jacoby 2NT
                        return (2, Suit.NOTRUMP)
                else:
                    # 2 over 1
                    if suitA.value < suit.value:
                        return (2, suitA)
                    if suitB.value < suit.value:
                        return (2, suitB)
                    return (2, Suit.CLUB)
        else:
            # Do not have support for opener's major
            if hcPts < 6:
                return (0, Suit.ALL)
            if hcPts < 9 and table.competition:
                return (0, Suit.ALL)

            if totalPts >= 6 and totalPts <= 12:
                if suit == Suit.HEART:
                    (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
                    if numSpades >= 4:
                        return (1, Suit.SPADE)
                return (1, Suit.NOTRUMP)

            if totalPts >= 15 and totalPts <= 17:
                if player.hand.isHandBalanced() and player.hand.hasStoppers() and numBidSuit >= 2:
                    return (3, Suit.NOTRUMP)

            if totalPts >= 13:
                # 2 over 1
                if suitA.value < suit.value:
                    return (2, suitA)
                if suitB.value < suit.value:
                    return (2, suitB)
                return (2, Suit.CLUB)

    @ResponderFunctions.register(command="rsp_1NT")    
    def open1NoTrumpRsp(self, table, player):
        writeLog(table, "responderBid: open1NoTrumpRsp by %s\n" % player.pos.name)
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        # Do I have a 5+ card major?
        (numHearts, numHighHearts) = player.hand.evalSuitStrength(Suit.HEART)
        if numHearts >= 5:
            # Jacoby transfer
            return (2, Suit.DIAMOND)
        
        (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
        if numSpades >= 5:
            # Jacoby transfer
            return (2, Suit.HEART)
        
        if hcPts < 8:
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if numCardsA >= 5 and suitA != Suit.CLUB:
                return (2, suitA)
            else:
                return (0, Suit.ALL)

        balancedHand = player.hand.isHandBalanced()
        if balancedHand:
            if numSpades >= 4 or numHearts >= 4:
                if hcPts >= 8 and hcPts <= 9:
                    return (2, Suit.NOTRUMP)
                elif hcPts >= 10 and hcPts <= 15:
                    return (3, Suit.NOTRUMP)
                elif hcPts >= 16 and hcPts <= 17:
                    return (4, Suit.NOTRUMP)
                elif hcPts >= 18 and hcPts <= 19:
                    return (6, Suit.NOTRUMP)
                elif hcPts >= 20 and hcPts <= 21:
                    return (5, Suit.NOTRUMP)
                elif hcPts >= 22:
                    return (7, Suit.NOTRUMP)

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if numSpades >= 6 or numHearts >= 6:
            if hcPts >= 10 and hcPts <= 15:
                return (4, suitA)

        (numDiamonds, numHighDiamonds) = player.hand.evalSuitStrength(Suit.DIAMOND)
        (numClubs, numHighClubs) = player.hand.evalSuitStrength(Suit.CLUB)
        if numDiamonds >= 6 or numClubs >= 6:
            return (3, Suit.NOTRUMP)

        if numSpades >= 4 or numHearts >= 4:
            return (2, Suit.CLUB)

        if numCardsA >= 5 and hcPts >= 10:
            return (3, suitA)

        if numSpades >= 5 or numHearts >= 5:
            if totalPts >= 8 and totalPts <= 9:
                return (2, Suit.CLUB)

        if hcPts >= 8 and hcPts <= 9:
            return (2, Suit.NOTRUMP)
        elif hcPts >= 10 and hcPts <= 15:
            return (3, Suit.NOTRUMP)
        elif hcPts >= 16 and hcPts <= 17:
            return (4, Suit.NOTRUMP)
        elif hcPts >= 18 and hcPts <= 19:
            return (6, Suit.NOTRUMP)
        elif hcPts >= 20 and hcPts <= 21:
            return (5, Suit.NOTRUMP)
        elif hcPts >= 22:
            return (7, Suit.NOTRUMP)

    @ResponderFunctions.register(command="rsp_2C")
    def open2ClubRsp(self, table, player):
        writeLog(table, "responderBid: open2ClubRsp by %s\n" % player.pos.name)
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        if hcPts < 8:
            return (2, Suit.DIAMOND)

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if numCardsA >= 5:
            if suitA == Suit.DIAMOND:
                return (3, suitA)
            else:
                return (2, suitA)

        balancedHand = player.hand.isHandBalanced()
        if balancedHand:
            return (2, Suit.NOTRUMP)

        return (2, Suit.DIAMOND)


    @ResponderFunctions.register(command="rsp_2Weak") 
    def openWeakRsp(self, table, player):
        writeLog(table, "responderBid: openWeakRsp by %s\n" % player.pos.name)
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
                return (2, Suit.NOTRUMP)
                
            if totalPts >= 8 and totalPts <= 13:
                # Bid 4                
                if level < 4:
                    return (4, suit)
                else:
                    return (0, Suit.ALL)
            
            if numCardsWeHave == 8:
                return (0, Suit.ALL)
            elif numCardsWeHave == 9:
                if level < 3:
                    return (3, suit)
                else:
                    return (0, Suit.ALL)
            elif numCardsWeHave >= 10:
                if level < 4:
                    return (4, suit)
                else:
                    return (0, Suit.ALL)
        else:
            # We don't have a fit. Pass if opened above the 2 level
            if level >= 3:
                return (0, Suit.ALL)

            # I can show a new 6 card suit           
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if numCardsA >= 6 and suitA.value > suit.value:
                return (level, suitA)
            if numCardsB >= 6 and suitB.value > suit.value:
                return (level, suitB)
            if numCardsA >= 6 and suitA > Suit.CLUB:
                return (3, Suit.CLUB)
            
            if player.hand.hasStoppers():
                numCardsOppHas = 13 - numCardsWeHave
                if highCardCount * 2 >= numCardOppHave:
                    return (3, Suit.NOTRUMP)

            # Can we bid a 5 card suit at the 2 level
            if hcPts >= 15 and numCardsA >= 5 and suitA.value < suit.value and level == 2:
                return (2, suitA)

            # Check if we should commit a sacrifice
            # Sacrifice if you will go down by no more than 2 tricks
            minTricks = 6 + level + 1 - 2
            # HACK: use a vastly simplified estimate of number of tricks we will take
            winTricks = 4 + int((totalPts + 8)/5)
            if winTricks >= minTricks:
                return (level+1, bidSuit)

        return (0, Suit.ALL)


    @ResponderFunctions.register(command="rsp_2NT")    
    def open2NoTrumpRsp(self, table, player):
        writeLog(table, "responderBid: open2NoTrumpRsp by %s\n" % player.pos.name)
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if hcPts < 5:
            if numCardsA >= 6:
                return (3, suitA)
            else:
                return (0, Suit.ALL)

        (numSpades, numHighSpades) = player.hand.evalSuitStrength(Suit.SPADE)
        (numHearts, numHighHearts) = player.hand.evalSuitStrength(Suit.HEART)        
        if hcPts >= 5 and hcPts <= 11:
            if numSpades >= 6 or numHearts >= 6:
                return (4, suitA)

        if hcPts >= 5:
            if numSpades >= 4 or numHearts >= 4:
                    return (3, Suit.CLUB)

        balancedHand = player.hand.isHandBalanced()
        if not balancedHand:
            if numCardsA >= 5 and suitA != Suit.CLUB:
                return (3, suitA)

        if numSpades >= 4 or numHearts >= 4:
            if hcPts >= 5 and hcPts <= 11:
                return (3, Suit.NOTRUMP)
            if hcPts == 12:
                return (4, Suit.NOTRUMP)
            if hcPts >= 13 and hcPts <= 15:
                return (6, Suit.NOTRUMP)
            if hcPts == 16:
                return (5, Suit.NOTRUMP)
            if hcPts >= 17:
                return (7, Suit.NOTRUMP)

    @ResponderFunctions.register(command="rsp_3NT")    
    def open3NoTrumpRsp(self, table, player):
        writeLog(table, "responderBid: open3NoTrumpRsp by %s\n" % player.pos.name)
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        if hcPts == 7:
            return (4, Suit.NOTRUMP)
        if hcPts >= 8 and hcPts <= 9:
            return (6, Suit.NOTRUMP)
        if hcPts >= 10 and hcPts <= 11:
            return (5, Suit.NOTRUMP)
        if hcPts >= 12:
            return (7, Suit.NOTRUMP)

def responderBid(self, table, player):
    # FIX ME: dead code
    print("responderBid: responderBid: ERROR?")
    hand = player.hand
    writeLog(table, "responderBid: bidsList={}\n".format(table.bidsList))
    # Extract opening bid from partner
    (openLevel, openSuit) = bidsList[-2]
    writeLog(table, "responderBid: openLevel=%d openSuit=%s\n" % (openLevel, openSuit))
    if openLevel == 1:
        if openSuit == Suit.CLUB or openSuit == Suit.DIAMOND:
            (bidLevel, bidSuit) = open1MinorRsp(table, player)
        elif openSuit == Suit.HEART or openSuit == Suit.SPADE:
            (bidLevel, bidSuit) = open1MajorRsp(table, player)
        elif openSuit == Suit.NOTRUMP:
            (bidLevel, bidSuit) = open1NoTrumpRsp(table, player)

    elif openLevel == 2:
        if openSuit == Suit.CLUB:
            (bidLevel, bidSuit) = open2ClubsRsp(table, player)
        elif openSuit == Suit.DIAMOND or openSuit == Suit.HEART or openSuit == Suit.SPADE:
            (bidLevel, bidSuit) = openWeakRsp(table, player)
        elif openSuit == Suit.NOTRUMP:
            (bidLevel, bidSuit) = open2NoTrumpRsp(hand)

    elif openLevel == 3:
        if openSuit == Suit.NOTRUMP:
            (bidLevel, bidSuit) = open3NoTrumpRsp(hand)
        else:
            (bidLevel, bidSuit) = openWeakRsp(table, player)

    elif openLevel == 4:
        if openSuit == Suit.NOTRUMP:
            (bidLevel, bidSuit) = open3NoTrumpRsp(hand)
        else:
            (bidLevel, bidSuit) = openWeakRsp(table, player)

    return (bidLevel, bidSuit)
    
