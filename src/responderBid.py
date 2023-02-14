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
    @ResponderFunctions.register(command="rsp_1Mi")
    def open1MinorRsp(self, table, player):
        writeLog(table, "responderBid: open1MinorRsp by %s" % player.pos.name)
        hand = player.hand
        suit = player.teamState.bidSeq[-1][1]
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        if hcPts < 6:
            return (0, Suit.ALL)
        if hcPts < 9 and table.competition:
            return (0, Suit.ALL)

        # Can we suggest a major?
        (numSpades, numHighSpades) = hand.evalSuitStrength(Suit.SPADE)
        (numHearts, numHighHearts) = hand.evalSuitStrength(Suit.HEART)
        if numSpades >= 4 or numHearts >= 4:
            if numSpades == 5 and numHearts == 5:
                return (1, Suit.SPADE)
            elif numSpades == 4 and numHearts == 4:
                return (1, Suit.HEART)
            elif numSpades > numHearts:
                return (1, Suit.SPADE)
            else:
                return (1, Suit.HEART)

        # Can we support the bid minor?
        (numMinor, numHighMinor) = hand.evalSuitStrength(suit)
        if numMinor >= 4:
            if totalPts >= 6 and totalPts <= 9:
                singleSuit = hand.hasSingletonOrVoid(suit)
                if numMinor >= 6 and singleSuit != Suit.ALL:
                    return (4, suit)
            return (2, suit)

            if totalPts >= 10 and totalPts <= 11:
                return (3, suit)
            else:
                # Bid a new suit
                if numSpades > numHearts:
                    return (1, Suit.SPADE)
                else:
                    return (1, Suit.HEART)
            return (1, suit)

        if totalPts >= 10:
            if hand.hasStoppers():
                balancedHand = hand.isHandBalanced()
                if hcpPts >= 16 and hcpPts <= 18 and balancedHand:
                    return (3, Suit.NOTRUMP)
                elif hcpPts >= 13 and hcpPts <= 15 and balancedHand:
                    return (2, Suit.NOTRUMP)

            (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
            if numCardsA >= 5 and numCardsA == numCardsB:
                # Bid the higher of the two suits
                if (suitA.value > suitB.value) and (suitA.value > suit.value):
                    return (1, suitA)
                elif (suitB.value > suit.value):
                    return (1, suitB)

            if numCardsA >= 4 and numCardsB >= 4:
                # Bid the lower of the two suits
                if suitA.value > suitB.value and suitB.value > suit.value:
                    return (1, suitB)
                elif suitA.value > suit.value:
                    return (1, suitA)

            if suitA.value > suit.value:
                return (1, suitA)
            elif suitB.value > suit.value:
                return (1, suitB)
            else:
                return (1, Suit.NOTRUMP)

        if (suit == Suit.CLUB) and (hand.numCardsInSuit(Suit.DIAMOND) >= 4):
            return (1, Suit.DIAMOND)
        else:
            return (1, Suit.NOTRUMP)

    @ResponderFunctions.register(command="rsp_1Ma")
    def open1MajorRsp(self, table, player):
        writeLog(table, "responderBid: open1MajorRsp by %s" % player.pos.name)
        hand = player.hand
        suit = player.teamState.bidSeq[-1][1]
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        if hcPts < 6:
            return (0, Suit.ALL)
        if hcPts < 9 and table.competition:
            return (0, Suit.ALL)

        # Can we support the bid suit?
        (numBidSuit, numHigh) = hand.evalSuitStrength(suit)
        if numBidSuit >= 3:
            if totalPts >= 6 and totalPts <= 9:
                singleSuit = hand.hasSingletonOrVoid(suit)
                if numMinor >= 5 and singleSuit != Suit.ALL:
                    return (4, suit)
            return (2, suit)

            if totalPts >= 10 and totalPts <= 11:
                return (2, suit)
            else:
                # Bid a new suit
                if suit == Suit.HEART:
                    return (1, Suit.SPADE)
                else:
                    return (1, Suit.NOTRUMP)

        if suit == Suit.HEART:
            (numSpades, numHighSpades) = hand.evalSuitStrength(Suit.SPADE)
            if numSpades >= 4:
                return (1, Suit.SPADE)

        if totalPts >= 10:
            (numHearts, numHighHearts) = hand.evalSuitStrength(Suit.HEART)
            if suit == Suit.SPADE and numHearts >= 4:
                return (2, Suit.HEART)

            if hand.hasStoppers():
                balancedHand = hand.isHandBalanced()
                if hcpPts >= 16 and hcpPts <= 18 and balancedHand:
                    return (3, Suit.NOTRUMP)
                elif hcpPts >= 13 and hcpPts <= 15 and balancedHand:
                    return (2, Suit.NOTRUMP)

            (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
            if numCardsA >= 5 and numCardsA == numCardsB:
                # Bid the higher of the two suits
                if suitA.value > suitB.value:
                    return (1, suitA)
                else:
                    return (1, suitB)

            if numCardsA >= 4 and numCardsB >= 4:
                # Bid the lower of the two suits
                if suitA.value > suitB.value:
                    return (1, suitB)
                else:
                    return (1, suitA)
            return (1, suitA)
        return (1, Suit.NOTRUMP)

    @ResponderFunctions.register(command="rsp_1NT")    
    def open1NoTrumpRsp(self, table, player):
        writeLog(table, "responderBid: open1NoTrumpRsp by %s" % player.pos.name)
        hand = player.hand
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        if hcPts < 8:
            (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
            if numCardsA >= 5 and suitA != Suit.CLUB:
                return (2, suitA)
            else:
                return (0, Suit.ALL)

        (numSpades, numHighSpades) = hand.evalSuitStrength(Suit.SPADE)
        (numHearts, numHighHearts) = hand.evalSuitStrength(Suit.HEART)        
        balancedHand = hand.isHandBalanced()
        if balancedHand:
            if numSpades >= 4 or numHearts >= 4:
                if hcpPts >= 8 and hcpPts <= 9:
                    return (2, Suit.NOTRUMP)
                elif hcpPts >= 10 and hcpPts <= 15:
                    return (3, Suit.NOTRUMP)
                elif hcpPts >= 16 and hcpPts <= 17:
                    return (4, Suit.NOTRUMP)
                elif hcpPts >= 18 and hcpPts <= 19:
                    return (6, Suit.NOTRUMP)
                elif hcpPts >= 20 and hcpPts <= 21:
                    return (5, Suit.NOTRUMP)
                elif hcpPts >= 22:
                    return (7, Suit.NOTRUMP)

        (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
        if numSpades >= 6 or numHearts >= 6:
            if hcpPts >= 10 and hcpPts <= 15:
                return (4, suitA)

        (numDiamonds, numHighDiamonds) = hand.evalSuitStrength(Suit.DIAMOND)
        (numClubs, numHighClubs) = hand.evalSuitStrength(Suit.CLUB)
        if numDiamonds >= 6 or numClubs >= 6:
            return (3, Suit.NOTRUMP)

        if numSpades >= 4 or numHearts >= 4:
            return (2, Suit.CLUB)

        if numCardsA >= 5 and hcPts >= 10:
            return (3, suitA)

        if numSpades >= 5 or numHearts >= 5:
            if totalPts >= 8 and totalPts <= 9:
                return (2, Suit.CLUB)

        if hcpPts >= 8 and hcpPts <= 9:
            return (2, Suit.NOTRUMP)
        elif hcpPts >= 10 and hcpPts <= 15:
            return (3, Suit.NOTRUMP)
        elif hcpPts >= 16 and hcpPts <= 17:
            return (4, Suit.NOTRUMP)
        elif hcpPts >= 18 and hcpPts <= 19:
            return (6, Suit.NOTRUMP)
        elif hcpPts >= 20 and hcpPts <= 21:
            return (5, Suit.NOTRUMP)
        elif hcpPts >= 22:
            return (7, Suit.NOTRUMP)

    @ResponderFunctions.register(command="rsp_2C")
    def open2ClubRsp(self, table, player):
        writeLog(table, "responderBid: open2ClubRsp by %s" % player.pos.name)
        hand = player.hand
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        if hcPts < 8:
            return (2, Suit.DIAMOND)

        (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
        if numCardsA >= 5:
            if suitA == Suit.DIAMOND:
                return (3, suitA)
            else:
                return (2, suitA)

        balancedHand = hand.isHandBalanced()
        if balancedHand:
            return (2, Suit.NOTRUMP)

        return (2, Suit.DIAMOND)


    @ResponderFunctions.register(command="rsp_2Weak") 
    def openWeakRsp(self, table, player):
        writeLog(table, "responderBid: openWeakRsp by %s" % player.pos.name)
        hand = player.hand
        # Get the bid from my partner
        level = player.teamState.bidSeq[-1][0]
        suit = player.teamState.bidSeq[-1][1]
        
        # How many points do I have?
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        (category, numCardsIHave, highCardCount) = hand.evalSuitCategory(suit)
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
            (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
            if numCardsA >= 6 and suitA.level > suit.level:
                return (level, suitA)
            if numCardsB >= 6 and suitB.level > suit.level:
                return (level, suitB)
            if numCardsA >= 6 and suitA > Suit.CLUB:
                return (3, Suit.CLUB)
            
            if hand.hasStoppers():
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
        writeLog(table, "responderBid: open2NoTrumpRsp by %s" % player.pos.name)
        hand = player.hand
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        (suitA, numCardsA, suitB, numCardsB) = hand.numCardsInTwoLongestSuits()
        if hcPts < 5:
            if numCardsA >= 6:
                return (3, suitA)
            else:
                return (0, Suit.ALL)

        (numSpades, numHighSpades) = hand.evalSuitStrength(Suit.SPADE)
        (numHearts, numHighHearts) = hand.evalSuitStrength(Suit.HEART)        
        if hcPts >= 5 and hcPts <= 11:
            if numSpades >= 6 or numHearts >= 6:
                return (4, suitA)

        if hcPts >= 5:
            if numSpades >= 4 or numHearts >= 4:
                    return (3, Suit.CLUB)

        balancedHand = hand.isHandBalanced()
        if not balancedHand:
            if numCardsA >= 5 and suitA != Suit.CLUB:
                return (3, suitA)

        if numSpades >= 4 or numHearts >= 4:
            if hcpPts >= 5 and hcpPts <= 11:
                return (3, Suit.NOTRUMP)
            if hcpPts == 12:
                return (4, Suit.NOTRUMP)
            if hcpPts >= 13 and hcpPts <= 15:
                return (6, Suit.NOTRUMP)
            if hcpPts == 16:
                return (5, Suit.NOTRUMP)
            if hcpPts >= 17:
                return (7, Suit.NOTRUMP)

    @ResponderFunctions.register(command="rsp_3NT")    
    def open3NoTrumpRsp(self, table, player):
        writeLog(table, "responderBid: open3NoTrumpRsp by %s" % player.pos.name)
        hand = player.hand
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        if hcpPts == 7:
            return (4, Suit.NOTRUMP)
        if hcpPts >= 8 and hcpPts <= 9:
            return (6, Suit.NOTRUMP)
        if hcpPts >= 10 and hcpPts <= 11:
            return (5, Suit.NOTRUMP)
        if hcpPts >= 12:
            return (7, Suit.NOTRUMP)

def responderBid(self, table, player):
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
    
