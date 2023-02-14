'''
Functions used for generating bids by the opener after getting
a responding bid from the partner
'''

from enums import Suit, Level, DistMethod
from utils import *
from card import Card
from cardPile import CardPile
from methodRegistry import MethodRegistry


class OpenerRebidRegistry:
    # Create a registry of functions used by the potential opener
    class OpenerFunctions(MethodRegistry):
        pass

    def __init__(self):
        # Bind methods to instance
        self.jump_table = OpenerRegistry.OpenerFunctions.get_bound_jump_table(self)


    # Define functions

    @OpenerFunctions.register(command="openRebid_undefined")
    def openRebid_undefined(self, table, player):
        writeLog(table, "openRebid_undefined by %s" % player.pos.name)
        print("openRebid found an undefined bidding sequence: {}".format(player.teamState.bidSeq))
        return (0, Suit.ALL)
    
    @OpenerFunctions.register(command="openRebid")
    def openRebid(table, hand, bidsList):
        print("openRebid: openRebid: entry")
        writeLog(table, "openRebid: bidsList={}\n".format(bidsList))
        # Extract responding bid from partner
        (rspLevel, rspSuit) = bidsList[-2]
        writeLog(table, "responderBid: rspLevel=%d rspSuit=%s\n" % (rspLevel, rspSuit))
        if rspLevel == 1:
            if rspSuit == Suit.CLUB or rspSuit == Suit.DIAMOND:
                (bidLevel, bidSuit) = rsp1MinorRsp(table, hand, rspSuit)
            elif rspSuit == Suit.HEART or rspSuit == Suit.SPADE:
                (bidLevel, bidSuit) = rsp1MajorRsp(hand, rspSuit)
            elif rspSuit == Suit.NOTRUMP:
                (bidLevel, bidSuit) = rsp1NoTrumpRsp(hand)

        elif rspLevel == 2:
            if rspSuit == Suit.CLUB:
                (bidLevel, bidSuit) = rsp2ClubsRsp(hand, rspSuit)
            elif rspSuit == Suit.DIAMOND or rspSuit == Suit.HEART or rspSuit == Suit.SPADE:
                (bidLevel, bidSuit) = rspWeakRsp(hand, rspSuit, 2)
            elif rspSuit == Suit.NOTRUMP:
                (bidLevel, bidSuit) = rsp2NoTrumpRsp(hand)

        elif rspLevel == 3:
            if rspSuit == Suit.NOTRUMP:
                (bidLevel, bidSuit) = rsp3NoTrumpRsp(hand)
            else:
                (bidLevel, bidSuit) = rspWeakRsp(hand, rspSuit, 3)

        elif rspLevel == 4:
            if rspSuit == Suit.NOTRUMP:
                (bidLevel, bidSuit) = rsp3NoTrumpRsp(hand)
            else:
                (bidLevel, bidSuit) = rspWeakRsp(hand, rspSuit, 4)

        return (bidLevel, bidSuit)
        
    @OpenerFunctions.register(command="openRebid_1_Pass")
    def openRebid_1_Pass(self, table, player):
        writeLog(table, "openRebid_1_Pass by %s" % player.pos.name)
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        # Sanity check
        if suitA != openingSuit:
            print("openerRebid_1_Pass: openSuit=%s longSuit=%d" % (openingSuit.name, suitA.name))

        # Do I have a second suit
        secondSuit = Suit.ALL
        if isMinor(suitB) and numCardsB >= 5 and suitB.level > openingSuit.level:
            secondSuit = suitB
        elif isMajor(suitB) and numCardsB >= 4:
            secondSuit = suitB
        
        if totalPts >= 13 and totalPts <= 15:
            if secondSuit != Suit.ALL:
                return (1, secondSuit)
            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                return (2, openingSuit)
            if table.competition:
                return (0, Suit.ALL)
            return (1, Suit.NOTRUMP)
        elif totalPts >= 16 and totalPts <= 18:
            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                return (3, openingSuit)
            if secondSuit != Suit.ALL:
                return (1, secondSuit)
            return (1, Suit.NOTRUMP)
        elif totalPts >= 19 and totalPts <= 21:
            if isMinor(suitB) and numCardsB >= 5 or isMajor(suitB) and numCardsB >= 4:
                # Bid a jump shift of second suit
                if suitB.level > openingSuit.level:
                    return (2, secondSuit)
                else:
                    return (3, secondSuit)

            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                return (3, Suit.NOTRUMP)

            if player.hand.isHandBalanced():
                if hcPts >= 20:
                    return (3, Suit.NOTRUMP)
                if hcPts >= 18:
                    return (2, Suit.NOTRUMP)
            else:
                if player.hand.getNumCardsInSuit(openingSuit) >= 7:
                    # Bid game
                    if openingSuit.isMajor():
                        return (4, openingSuit)
                    else:
                        return (5, openingSuit)
                elif player.hand.getNumCardsInSuit(openingSuit) >= 6:
                    return (3, openingSuit)
            return (2, Suit.NOTRUMP)
        print("openRebid_1_Pass: ERROR - should not reach here")
        

    @OpenerFunctions.register(command="openRebid_1C_1D")
    def openRebid_1C_1D(self, table, player):
        writeLog(table, "openRebid_1C_1D by %s" % player.pos.name)
        # How many points do I have?
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        # How many cards do I have in partner's suit
        (numCardsIHave, numHighCards) = player.hand.evalSuitStrength(Suit.DIAMOND)

        if totalPts >= 13 and totalPts <= 15:
            if numCardsIHave >= 4:
                return (2, Suit.DIAMOND)
            else:
                return (1, Suit.NOTRUMP)
        elif totalPts >= 16 and totalPts <= 18:
            if numCardsIHave >= 4:
                return (3, Suit.DIAMOND)
            # Do I have 6+ clubs?
            if player.hand.getNumCardsInSuit(Suit.CLUB) >= 6:
                return (3, Suit.CLUB)
            if totalPts == 18:
                return (2, Suit.NOTRUMP)
            return (1, Suit.NOTRUMP)
        elif totalPts >= 19 and totalPts <= 21:
            if numCardsIHave >= 4:
                return (4, Suit.DIAMOND)
            # Do I have 6+ clubs?
            if player.hand.getNumCardsInSuit(Suit.CLUB) >= 6:
                return (4, Suit.CLUB)
            return (3, Suit.NOTRUMP)
        
        print("openRebid_1C_1D: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1Mi_1Ma")
    def openRebid_1Mi_1Ma(self, table, player):
        writeLog(table, "openRebid_1Mi_1Ma by %s" % player.pos.name)

        # How many points do I have?
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        openingSuit = player.teamState.candidateSuit
        numCardsInSuit = player.hand.numCardsInSuit(openingSuit)
        
        # How many cards do I have in partner's suit
        partnerSuit = player.teamState.bidSeq[-1][1]
        (numCardsIHave, numHighCards) = player.hand.evalSuitStrength(partnerSuit)
        numSpades = 0
        if partnerSuit == Suit.HEART:
            numSpades = player.hand.numCardsInSuit(Suit.SPADES)

        if totalPts >= 13 and totalPts <= 15:
            if numCardsIHave >= 4:
                return (2, partnerSuit)
            if numSpades >= 4:
                return (1, Suit.SPADES)
            if numCardsInSuit >= 6:
                return (2, openingSuit)
            if table.competition:
                return (0, Suit.ALL)
            return (1, Suit.NOTRUMP)

        elif totalPts >= 16 and totalPts <= 18:
            if numCardsIHave >= 4:
                return (3, partnerSuit)
            if player.hand.isHandBalanced():
                if hcPts >= 18:
                    return (2, Suit.NOTRUMP)
            if numCardsInSuit >= 6:
                return (3, openingSuit)
            if numSpades >= 4:
                return (2, Suit.SPADES)
            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.numCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 4:
                    return (2, Suit.CLUB)
            return (2, Suit.NOTRUMP)
        
        elif totalPts >= 19 and totalPts <= 21:
            if numCardsIHave >= 4:
                return (4, partnerSuit)
            if player.hand.isHandBalanced():
                return (3, Suit.NOTRUMP)
            if numCardsInSuit >= 6:
                return (2, Suit.NOTRUMP)
            if numSpades >= 4:
                return (3, Suit.SPADES)
            return (3, Suit.NOTRUMP)
        print("openRebid_1Mi_1Ma: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1H_1S")
    def openRebid_1H_1S(self, table, player):
        writeLog(table, "openRebid_1H_1S by %s" % player.pos.name)

        # How many points do I have?
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        # How many cards do I have in partner's suit
        partnerSuit = player.teamState.bidSeq[-1][1]
        (numCardsIHave, numHighCards) = player.hand.evalSuitStrength(partnerSuit)

        if totalPts >= 13 and totalPts <= 15:
            if numCardsIHave >= 4:
                return (2, partnerSuit)
            if player.hand.isHandBalanced():
                return (1, Suit.NOTRUMP)
            
            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.numCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                return (2, openingSuit)

            return (1, Suit.NOTRUMP)

        elif totalPts >= 16 and totalPts <= 18:
            if numCardsIHave >= 4:
                return (3, partnerSuit)

            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.numCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                return (3, openingSuit)
            
            if player.hand.isHandBalanced() and totalPts == 18:
                return (2, Suit.NOTRUMP)
            
            return (1, Suit.NOTRUMP)
        
        elif totalPts >= 19 and totalPts <= 21:
            if numCardsIHave >= 4:
                return (4, partnerSuit)
            
            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.numCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                return (4, openingSuit)

            return (3, Suit.NOTRUMP)
        
        print("openRebid_1H_1S: ERROR - should not reach here")

        
    @OpenerFunctions.register(command="openRebid_1Mi_1NT")
    def openRebid_1Mi_1NT(self, table, player):
        writeLog(table, "openRebid_1Mi_1NT by %s" % player.pos.name)

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts >= 13 and totalPts <= 15:
            if player.hand.isHandBalanced():
                return (0, Suit.ALL)
            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.numCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 4:
                    return (2, Suit.CLUB)
                numCardsInSuit = player.hand.numCardsInSuit(Suit.DIAMOND)
                if numCardsInSuit >= 6:
                    return (2, Suit.DIAMOND)
            elif openingSuit == Suit.CLUB:
                numCardsInSuit = player.hand.numCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 5:
                    return (2, Suit.CLUB)
            return (0, Suit.ALL)
            
        elif totalPts >= 16 and totalPts <= 18:
            if player.hand.isHandBalanced():
                return (2, Suit.NOTRUMP)
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                return (2, suitA)
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                return (2, suitA)
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                return (2, suitB)
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                return (2, suitB)
            
            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.numCardsInSuit(Suit.DIAMOND)
                if numCardsInSuit >= 6:
                    return (3, Suit.DIAMOND)
            elif openingSuit == Suit.CLUB:
                numCardsInSuit = player.hand.numCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 5:
                    return (3, Suit.CLUB)
            return (2, Suit.NOTRUMP)
        
        elif totalPts >= 19 and totalPts <= 21:
            if player.hand.isHandBalanced():
                return (3, Suit.NOTRUMP)
            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.numCardsInSuit(Suit.DIAMOND)
                if numCardsInSuit >= 6:
                    return (4, Suit.DIAMOND)
            elif openingSuit == Suit.CLUB:
                numCardsInSuit = player.hand.numCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 5:
                    return (4, Suit.CLUB)

            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                return (3, suitA)
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                return (3, suitA)
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                return (3, suitB)
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                return (3, suitB)
            return (3, Suit.NOTRUMP)
        print("openRebid_1Mi_1NT: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_1Mi_nMi")
    def openRebid_1Mi_nMi(self, table, player):
        writeLog(table, "openRebid_1Mi_nMi by %s" % player.pos.name)

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]
        if partnerLevel < 2 or partnerLevel > 3:
            print("openRebid: 1Mi_nMi: ERROR-partner level %d" % partnerLevel)    
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts >= 13 and totalPts <= 15:
            return (0, Suit.ALL)
        
        elif totalPts >= 16 and totalPts <= 18:
            if partnerLevel == 2:
                return (3, openingSuit)
            elif partnerLevel == 3:
                return (2, Suit.NOTRUMP)
            
        elif totalPts >= 19 and totalPts <= 21:
            if partnerLevel == 2:
                if player.hand.hasStoppers():
                    return (3, Suit.NOTRUMP)
                if totalPts == 21:
                    return (4, openingSuit)
                else:
                    return (3, openingSuit)                    
            elif partnerLevel == 3:
                if player.hand.hasStoppers():
                    return (3, Suit.NOTRUMP)
                else:
                    return (2, Suit.NOTRUMP)
        
        print("openRebid_1Mi_nMi: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1Ma_nMa")
    def openRebid_1Ma_nMa(self, table, player):
        writeLog(table, "openRebid_1Ma_nMa by %s" % player.pos.name)

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]
        if partnerLevel < 2 or partnerLevel > 4:
            print("openRebid: 1Ma_nMa: ERROR-partner level %d" % partnerLevel)    
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if partnerLevel == 4:
            return (0, Suit.ALL)
        if partnerLevel == 3:
            if totalPts >= 13 and totalPts <= 14:
                return (0, Suit.ALL)
            if totalPts >= 15 and totalPts <= 19:
                return (4, openingSuit)
            else:
                # Blackwood
                return (4, Suit.NOTRUMP)
        # Partner level = 2
        if totalPts >= 13 and totalPts <= 15:
            return (0, Suit.ALL)
        if totalPts >= 16 and totalPts <= 18:
            return (3, openingSuit)
        if totalPts >= 19 and totalPts <= 21:
            return (4, openingSuit)
        
        print("openRebid_1Ma_nMa: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1Ma_1NT")
    def openRebid_1Ma_1NT(self, table, player):
        writeLog(table, "openRebid_1Ma_1NT by %s" % player.pos.name)

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.numCardsInSuit(openingSuit)

        if totalPts >= 13 and totalPts <= 15:
            if numCardsInSuit >= 6:
                return (2, openingSuit)
            numMinor = player.hand.numCardsInSuit(Suit.DIAMOND)
            if numMinor >= 4:
                return (2, Suit.DIAMOND)
            numMinor = player.hand.numCardsInSuit(Suit.CLUB)
            if numMinor >= 3:
                return (2, Suit.CLUB)

            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                return (2, suitA)
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                return (2, suitA)
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                return (2, suitB)
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                return (2, suitB)
        
        elif totalPts >= 16 and totalPts <= 18:
            if numCardsInSuit >= 6:
                return (3, openingSuit)
            numMinor = player.hand.numCardsInSuit(Suit.DIAMOND)
            if numMinor >= 4:
                return (3, Suit.DIAMOND)
            numMinor = player.hand.numCardsInSuit(Suit.CLUB)
            if numMinor >= 3:
                return (3, Suit.CLUB)

            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                return (3, suitA)
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                return (3, suitA)
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                return (3, suitB)
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                return (3, suitB)
        
        elif totalPts >= 19 and totalPts <= 21:
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                return (3, suitA)
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                return (3, suitA)
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                return (3, suitB)
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                return (3, suitB)
            if numCardsInSuit >= 6 and player.hand.hasStoppers():
                return (3, Suit.NOTRUMP)
            if hcPts >= 18 and hcPts <= 19 and player.hand.isBalanced():
                return (3, Suit.NOTRUMP)
            if numCardsInSuit >= 7:
                return (4, openingSuit)
            if numCardsInSuit >= 6:
                return (3, openingSuit)
            return (3, Suit.NOTRUMP)
        print("openRebid_1Ma_1NT: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_1Ma_4W")
    def openRebid_1Ma_4W(self, table, player):
        writeLog(table, "openRebid_1Ma_4W by %s" % player.pos.name)
        # Splinter
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.numCardsInSuit(openingSuit)

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]
        
        if totalPts >= 13 and totalPts <= 16:
            if openingSuit == Suit.HEART and partnerSuit == Suit.SPADE:
                return (5, Suit.HEART)
            else:
                return (4, openingSuit)
        # Blackwood
        return (4, Suit.NOTRUMP)
    
    @OpenerFunctions.register(command="openRebid_1Mi_nNT")
    def openRebid_1Mi_nNT(self, table, player):
        writeLog(table, "openRebid_1Mi_nNT by %s" % player.pos.name)

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]
        if partnerLevel < 2 or partnerLevel > 3:
            print("openRebid: 1Mi_nNT: ERROR-partner level %d" % partnerLevel)
        if partnerLevel == 3:
            # Gerber
            return (4, Suit.CLUB)
        
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.numCardsInSuit(openingSuit)

        if totalPts >= 13 and totalPts <= 17:
            if player.hand.isBalanced():
                return (3, Suit.NOTRUMP)
            if openingSuit == Suit.DIAMOND and numCardsInSuit >= 6:
                return (3, Suit.DIAMOND)
            if openingSuit == Suit.CLUB and numCardsInSuit >= 5:
                return (3, Suit.CLUB)
        elif totalPts >= 18 and totalPts <= 21:
            # Gerber
            return (4, Suit.CLUB)
        
        print("openRebid_1Mi_nNT: ERROR - should not reach here")


    # Jacoby 2NT    
    def openRebid_1Ma_2NT(self, table, player):
        writeLog(table, "openRebid_1Ma_2NT by %s" % player.pos.name)

        # Do I have a singleton or void?
        openingSuit = player.teamState.candidateSuit
        singleSuit = player.hand.hasSingletonOrVoid(openingSuit)
        if singleSuit != Suit.ALL:
            return (3, singleSuit)
        
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts >= 13 and totalPts <= 15:
            return (4, openingSuit)
        
        elif totalPts >= 16 and totalPts <= 18:
            return (3, Suit.NOTRUMP)
            
        elif totalPts >= 19 and totalPts <= 21:
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 4:
                return (4, suitA)
            elif suitB != openingSuit and isMinor(suitB) and numCardsB >= 4:
                return (4, suitB)
            else:
                return (3, openingSuit)
        
        print("openRebid_1Ma_2NT: ERROR - should not reach here")

        
    def openRebid_1Ma_3NT(self, table, player):
        writeLog(table, "openRebid_1Ma_3NT by %s" % player.pos.name)

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts >= 13 and totalPts <= 14:
            return (0, Suit.ALL)

        # Explore slam with Gerber
        return (4, Suit.CLUB)
        
        print("openRebid_1Ma_3NT: ERROR - should not reach here")
        
        
    @OpenerFunctions.register(command="openRebid_2_over_1")
    def openRebid_2_over_1(self, table, player):
        writeLog(table, "openRebid_2_over_1 by %s" % player.pos.name)

        openingSuit = player.teamState.candidateSuit
        
        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]
        if partnerSuit.level > openingSuit.level:
            print("2_over_1: ERROR-partner did not bid under opening suit")
            
        # How many points do I have?
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.numCardsInSuit(openingSuit)

        if totalPts >= 13 and totalPts <= 15:
            if numCardsInSuit >= 6:
                return (2, openingSuit)
            numCardsInSuit = player.hand.numCardsInSuit(partnerSuit)
            if partnerSuit == Suit.CLUB and numCardsInSuit >= 5:
                return (3, partnerSuit)
            if partnerSuit == Suit.DIAMOND and numCardsInSuit >= 4:
                return (3, partnerSuit)
            if partnerSuit.isMajor() and numCardsInSuit >= 4:
                return (3, partnerSuit)
            return (3, Suit.NOTRUMP)
        
        elif totalPts >= 16 and totalPts <= 18:
            if numCardsInSuit >= 6:
                return (3, openingSuit)
            numCardsInSuit = player.hand.numCardsInSuit(partnerSuit)
            if partnerSuit == Suit.CLUB and numCardsInSuit >= 5:
                return (4, partnerSuit)
            if partnerSuit == Suit.DIAMOND and numCardsInSuit >= 4:
                return (4, partnerSuit)
            if partnerSuit.isMajor() and numCardsInSuit >= 4:
                return (4, partnerSuit)
            return (3, Suit.NOTRUMP)

        elif totalPts >= 19 and totalPts <= 21:
            # Bid jump shift
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and suitA != partnerSuit:
                if suitA.level > partnerSuit.level:
                    return (partnerSuit.level + 1, suitA)
                else:
                    return (partnerSuit.level + 2, suitA)
            if suitB != openingSuit and suitB != partnerSuit:
                if suitB.level > partnerSuit.level:
                    return (partnerSuit.level + 1, suitB)
                else:
                    return (partnerSuit.level + 2, suitB)
                
        print("openRebid_2_over_1: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_1NT_Pass")
    def openRebid_1NT_Pass(self, table, player):
        writeLog(table, "openRebid_1NT_Pass by %s" % player.pos.name)
        return (0, Suit.ALL)

    @OpenerFunctions.register(command="openRebid_1NT_2C")
    def openRebid_1NT_2C(self, table, player):
        writeLog(table, "openRebid_1NT_2C by %s" % player.pos.name)
        # Stayman
        numHearts = player.hand.numCardsInSuit(Suit.HEART)
        numSpades = player.hand.numCardsInSuit(Suit.SPADE)

        if numHearts < 4 and numSpades < 4:
            return (2, Suit.DIAMOND)
        if numHearts == 4 and numSpades == 4:
            return (2, Suit.HEART)
        if numHearts == 5 and numSpades == 5:
            return (2, Suit.SPADE)
        if numHearts > numSpades:
            return (2, Suit.HEART)
        else:
            return (2, Suit.SPADE)
        
        print("openRebid_1NT_2C: ERROR - should not reach here")
    
    @OpenerFunctions.register(command="openRebid_1NT_2W")
    def openRebid_1NT_2W(self, table, player):
        writeLog(table, "openRebid_1NT_2W by %s" % player.pos.name)

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many points do I have?
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        # Jacoby transfer
        if partnerSuit == Suit.DIAMOND:
            bidSuit = Suit.HEART
            bidLevel = 2
        elif partnerSuit == Suit.HEART:
            bidSuit = Suit.SPADE
            bidLevel = 2
        elif partnerSuit == Suit.SPADE:
            bidSuit = Suit.CLUB
            bidLevel = 3
        else:
            print("openerRebid_1NT_2W: ERROR-called with 2C response")

        if totalPts >= 17 and bidSuit != Suit.CLUB:
            numCardsInSuit = player.hand.numCardsInSuit(bidSuit)
            if numCardsInSuit >= 4:
                bidLevel += 1

        return (bidLevel, bidSuit)
        print("openRebid_1NT_2W: ERROR - should not reach here")


    @OpenerFunctions.register(command="openRebid_1NT_nNT")
    def openRebid_1NT_nNT(self, table, player):
        writeLog(table, "openRebid_1NT_nNT by %s" % player.pos.name)

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        
        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]

        if partnerLevel == 2:
            if hcPts > 15:
                return (3, Suit.NOTRUMP)
            else:
                return (0, Suit.ALL)
        elif partnerLevel == 3:
            return (0, Suit.ALL)
        elif partnerLevel == 4:
            if hcPts > 15:
                return (3, Suit.NOTRUMP)
            else:
                return (0, Suit.ALL)
        elif partnerLevel == 5:
            # Gerber
            return (6, Suit.CLUB)
        else:
            return (0, Suit.ALL)
           
    @OpenerFunctions.register(command="openRebid_1NT_3Mi")
    def openRebid_1NT_3Mi(self, table, player):
        writeLog(table, "openRebid_1NT_3Mi by %s" % player.pos.name)

        numHearts = player.hand.numCardsInSuit(Suit.HEART)
        numSpades = player.hand.numCardsInSuit(Suit.SPADE)

        if numHearts < 4 and numSpades < 4:
            return (3, Suit.NOTRUMP)
        if numHearts == 4 and numSpades == 4:
            return (3, Suit.HEART)
        if numHearts == 5 and numSpades == 5:
            return (3, Suit.SPADE)
        if numHearts > numSpades:
            return (3, Suit.HEART)
        else:
            return (3, Suit.SPADE)
        
        print("openRebid_1NT_3Mi: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1NT_3Ma")
    def openRebid_1NT_3Ma(self, table, player):
        writeLog(table, "openRebid_1NT_3Ma by %s" % player.pos.name)

        numHearts = player.hand.numCardsInSuit(Suit.HEART)
        numSpades = player.hand.numCardsInSuit(Suit.SPADE)

        if numHearts < 3 and numSpades < 3:
            return (3, Suit.NOTRUMP)
        if numHearts == 3 and numSpades == 3:
            return (4, Suit.HEART)
        if numHearts == 4 and numSpades == 4:
            return (4, Suit.HEART)
        if numHearts == 5 and numSpades == 5:
            return (4, Suit.SPADE)
        if numHearts > numSpades:
            return (4, Suit.HEART)
        else:
            return (3, Suit.SPADE)
        
        print("openRebid_1NT_3Ma: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_1NT_4Ma")
    def openRebid_1NT_4Ma(self, table, player):
        writeLog(table, "openRebid_1NT_4Ma by %s" % player.pos.name)

        # Not enough for slam
        return (0, Suit.ALL)


    @OpenerFunctions.register(command="openRebid_2C_2D")
    def openRebid_2C_2D(self, table, player):
        writeLog(table, "openRebid_2C_2D by %s" % player.pos.name)

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        
        if suitA.isMajor():
            if numCardsA >= 5:
                return (2, suitA)
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                return (2, suitB)
        if suitA.isMinor():
            if numCardsA >= 5:
                return (3, suitA)
            elif numCardsA == numCardsB:
                return (3, suitA)
            else:
                # 3 and 3 in the minors. Bid clubs
                return (3, suitB)
        print("openRebid_2C_2D: ERROR - should not reach here")


    @OpenerFunctions.register(command="openRebid_2C_2Ma")
    def openRebid_2C_2Ma(self, table, player):
        writeLog(table, "openRebid_2C_2Ma by %s" % player.pos.name)

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many cards do I have in partner's suit
        numCardsInSuit = player.hand.numCardsInSuit(partnerSuit)

        if numCardsInSuit >= 3:
            return (3, partnerSuit)
        
        # Find best suit to bid
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if suitA.isMajor():
            if numCardsA >= 5:
                return (2, suitA)
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                return (2, suitB)
        if suitA.isMinor():
            if numCardsA >= 5:
                return (3, suitA)
            elif numCardsA == numCardsB:
                return (3, suitA)
            else:
                # 3 and 3 in the minors. Bid clubs
                return (3, suitB)
        print("openRebid_2C_2Ma: ERROR - should not reach here")

        
    @OpenerFunctions.register(command="openRebid_2C_2NT")
    def openRebid_2C_2NT(self, table, player):
        writeLog(table, "openRebid_2C_2NT by %s" % player.pos.name)

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        
        if suitA.isMajor():
            if numCardsA >= 5:
                return (3, suitA)
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                return (3, suitB)
        if suitA.isMinor():
            if numCardsA >= 5:
                return (3, suitA)
            elif numCardsA == numCardsB:
                return (3, suitA)
            else:
                # 3 and 3 in the minors. Bid clubs
                return (3, suitB)
        print("openRebid_2C_2NT: ERROR - should not reach here")


    @OpenerFunctions.register(command="openRebid_2C_3Mi")
    def openRebid_2C_3Mi(self, table, player):
        writeLog(table, "openRebid_2C_3Mi by %s" % player.pos.name)

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many cards do I have in partner's suit
        numCardsInSuit = player.hand.numCardsInSuit(partnerSuit)

        if numCardsInSuit >= 3:
            return (4, partnerSuit)
        
        # Find best suit to bid
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if suitA.isMajor():
            if numCardsA >= 5:
                return (3, suitA)
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                return (3, suitB)
        if suitA.isMinor():
            if suitA == Suit.CLUB:
                return (4, suitA)
            else:
                return (3, suitA)

        print("openRebid_2C_3Mi: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_weak_Pass")
    def openRebid_weak_Pass(self, table, player):
        writeLog(table, "openRebid_weak_Pass by %s" % player.pos.name)
        return (0, Suit.ALL)
        
        
    @OpenerFunctions.register(command="openRebid_2weak_2W")
    def openRebid_2weak_2W(self, table, player):
        writeLog(table, "openRebid_2weak_2W by %s" % player.pos.name)
        
        openingSuit = player.teamState.candidateSuit

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many cards do I have in partner's suit
        numCardsInSuit = player.hand.numCardsInSuit(partnerSuit)

        if numCardsInSuit >= 2:
            return (0, Suit.ALL)
        return (3, openingSuit)
    
        print("openRebid_2weak_2W: ERROR - should not reach here")


    @OpenerFunctions.register(command="openRebid_2weak_2NT")
    def openRebid_2weak_2NT(self, table, player):
        writeLog(table, "openRebid_2weak_2NT by %s" % player.pos.name)

        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        
        if totalPts >= 10 and player.hand.hasStoppers():
            return (3, Suit.NOTRUMP)
        return (3, openingSuit)
        print("openRebid_2weak_2NT: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_2weak_3")
    def openRebid_2weak_3(self, table, player):
        writeLog(table, "openRebid_2weak_3 by %s" % player.pos.name)
        return (0, Suit.ALL)
        
    @OpenerFunctions.register(command="openRebid_2weak_3NT")
    def openRebid_weak_3NT(self, table, player):
        writeLog(table, "openRebid_2weak_3NT by %s" % player.pos.name)
        return (0, Suit.ALL)
        

    @OpenerFunctions.register(command="openRebid_2NT_3W")
    def openRebid_2NT_3W(self, table, player):
        writeLog(table, "openRebid_2NT_3W by %s" % player.pos.name)

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # Jacoby transfer
        if partnerSuit == Suit.DIAMOND:
            bidSuit = Suit.HEART
            bidLevel = 3
        elif partnerSuit == Suit.HEART:
            bidSuit = Suit.SPADE
            bidLevel = 3
        else:
            print("openerRebid_2NT_3W: ERROR-called with 2C response")

        return (bidLevel, bidSuit)
    
    @OpenerFunctions.register(command="openRebid_2NT_3W")
    def openRebid_2NT_3W(self, table, player):
        writeLog(table, "openRebid_2NT_3W by %s" % player.pos.name)

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # Jacoby transfer
        if partnerSuit == Suit.DIAMOND:
            bidSuit = Suit.HEART
            bidLevel = 3
        elif partnerSuit == Suit.HEART:
            bidSuit = Suit.SPADE
            bidLevel = 3
        else:
            print("openerRebid_2NT_3W: ERROR-called with 2C response")

        return (bidLevel, bidSuit)
    
    @OpenerFunctions.register(command="openRebid_2NT_3NT")
    def openRebid_2NT_3NT(self, table, player):
        writeLog(table, "openRebid_2NT_3NT by %s" % player.pos.name)
        return (0, Suit.ALL)

    @OpenerFunctions.register(command="openRebid_2NT_nNT")
    def openRebid_2NT_nNT(self, table, player):
        writeLog(table, "openRebid_2NT_nNT by %s" % player.pos.name)

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]

        if partnerLevel == 5:
            # Gerber
            return (6, Suit.CLUB)
        else:
            return (0, Suit.ALL)
        
    @OpenerFunctions.register(command="openRebid_3weak_3W")
    def openRebid_3weak_3W(self, table, player):
        writeLog(table, "openRebid_3weak_3W by %s" % player.pos.name)

        openingSuit = player.teamState.candidateSuit
        
        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many cards do I have in partner's suit
        numCardsInSuit = player.hand.numCardsInSuit(partnerSuit)

        if numCardsInSuit >= 3:
            if partnerSuit.isMajor():
                return (4, partnerSuit)
            else:
                return (0, Suit.ALL)
                
        return (4, openingSuit)
    
        print("openRebid_3weak_3W: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_3_4")
    def openRebid_3_4(self, table, player):
        writeLog(table, "openRebid_3_4 by %s" % player.pos.name)
        return (0, Suit.ALL)
        
    @OpenerFunctions.register(command="openRebid_3NT_nNT")
    def openRebid_3NT_nNT(self, table, player):
        writeLog(table, "openRebid_3NT_nNT by %s" % player.pos.name)

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]

        if partnerLevel == 4:
            # Gerber
            return (5, Suit.CLUB)
        elif partnerLevel == 5:
            return (6, Suit.NOTRUMP)
        else:
            return (0, Suit.ALL)
