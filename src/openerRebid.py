'''
Functions used for generating bids by the opener after getting
a responding bid from the partner
'''

from infoLog import Log
from enums import Suit, Level, DistMethod, FitState, Force
from utils import *
from card import Card
from cardPile import CardPile
from methodRegistry import MethodRegistry
from bidNotif import BidNotif


class OpenerRebidRegistry:
    # Create a registry of functions used by the potential opener
    class OpenerFunctions(MethodRegistry):
        pass

    def __init__(self):
        # Bind methods to instance
        self.jump_table = OpenerRebidRegistry.OpenerFunctions.get_bound_jump_table(self)


    # Define functions

    @OpenerFunctions.register(command="openRebid_undefined")
    def openRebid_undefined(self, table, player):
        Log.write("openRebid_undefined by %s\n" % player.pos.name)
        print("openRebid found an undefined bidding sequence: {}".format(player.teamState.bidSeq))
        return (0, Suit.ALL)

    # FIX ME: dead code?
    @OpenerFunctions.register(command="openRebid")
    def openRebid(table, hand, bidsList):
        Log.write("openRebid: bidsList={}\n".format(bidsList))
        # Extract responding bid from partner
        (rspLevel, rspSuit) = bidsList[-2]
        Log.write("responderBid: rspLevel=%d rspSuit=%s\n" % (rspLevel, rspSuit))
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
    
    @OpenerFunctions.register(command="openRebid_Pass_Pass")
    def openRebid_Pass_Pass(self, table, player):
        Log.write("openRebid_Pass_Pass by %s\n" % player.pos.name)
        bidLevel = 0
        bidSuit = Suit.ALL
        
        # Update the team state
        player.teamState.force = Force.PASS
        
        # Create a bid notification
        bidNotif = BidNotif(bidLevel, bidSuit, player.teamState)
        return bidNotif

        
    @OpenerFunctions.register(command="openRebid_1_Pass")
    def openRebid_1_Pass(self, table, player):
        Log.write("openRebid_1_Pass by %s\n" % player.pos.name)
        ts = player.teamState
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        # Sanity check
        if suitA != openingSuit:
            print("ERROR: openerRebid_1_Pass: openSuit=%s longSuit=%d" % (openingSuit.name, suitA.name))

        # Do I have a second suit
        secondSuit = Suit.ALL
        if isMinor(suitB) and numCardsB >= 5 and suitB.level > openingSuit.level:
            secondSuit = suitB
        elif isMajor(suitB) and numCardsB >= 4:
            secondSuit = suitB
        
        if totalPts <= 15:
            ts.myMaxPoints = 15
            if secondSuit != Suit.ALL:                
                ts.candidateSuit = secondSuit
                bidNotif = BidNotif(1, secondSuit, ts)
                return bidNotif
            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                bidNotif = BidNotif(2, openingSuit, ts)
                return bidNotif          
            if player.teamState.competition:
                bidNotif = BidNotif(0, Suit.ALL, ts)
                return bidNotif                
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
            return bidNotif                
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18
            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                bidNotif = BidNotif(3, openingSuit, ts)
                return bidNotif                
            if secondSuit != Suit.ALL:
                ts.candidateSuit = secondSuit
                bidNotif = BidNotif(1, secondSuit, ts)
                return bidNotif                
            bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
            return bidNotif                
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21
            if isMinor(suitB) and numCardsB >= 5 or isMajor(suitB) and numCardsB >= 4:
                # Bid a jump shift of second suit
                if suitB.level > openingSuit.level:
                    ts.candidateSuit = secondSuit
                    bidNotif = BidNotif(2, secondSuit, ts)
                    return bidNotif                
                else:
                    ts.candidateSuit = secondSuit
                    bidNotif = BidNotif(3, secondSuit, ts)
                    return bidNotif                

            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                return bidNotif                

            if player.hand.isHandBalanced():
                if hcPts >= 20:
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                    return bidNotif                
                if hcPts >= 18:
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
                    return bidNotif                
            else:
                if player.hand.getNumCardsInSuit(openingSuit) >= 7:
                    # Bid game
                    if openingSuit.isMajor():
                        bidNotif = BidNotif(4, openingSuit, ts)
                        return bidNotif                
                    else:
                        bidNotif = BidNotif(5, openingSuit, ts)
                        return bidNotif                
                elif player.hand.getNumCardsInSuit(openingSuit) >= 6:
                    bidNotif = BidNotif(3, openingSuit, ts)
                    return bidNotif                
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
            return bidNotif                
        print("openRebid_1_Pass: ERROR - should not reach here")
        

    @OpenerFunctions.register(command="openRebid_1C_1D")
    def openRebid_1C_1D(self, table, player):
        Log.write("openRebid_1C_1D by %s\n" % player.pos.name)
        ts = player.teamState        
        # How many points do I have?
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        # How many cards do I have in partner's suit
        (numCardsIHave, numHighCards) = player.hand.evalSuitStrength(Suit.DIAMOND)

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            ts.force = Force.NONE
            if numCardsIHave >= 4:
                # We have a fit in diamonds
                ts.fitSuit = Suit.DIAMOND
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(Suit.DIAMOND, FitState.SUPPORT)
                bidNotif = BidNotif(2, Suit.DIAMOND, ts)
                return bidNotif
            else:
                ts.setSuitState(Suit.DIAMOND, FitState.NO_SUPPORT)
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
                return bidNotif
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            ts.force = Force.NONE
            if numCardsIHave >= 4:
                # We have a fit in diamonds
                ts.fitSuit = Suit.DIAMOND
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(Suit.DIAMOND, FitState.SUPPORT)
                bidNotif = BidNotif(3, Suit.DIAMOND, ts)
                return bidNotif
            else:
                ts.setSuitState(Suit.DIAMOND, FitState.NO_SUPPORT)
            # Do I have 6+ clubs?
            if player.hand.getNumCardsInSuit(Suit.CLUB) >= 6:
                ts.candidateSuit = Suit.CLUB
                bidNotif = BidNotif(3, Suit.CLUB, ts)
                return bidNotif
            if totalPts == 18:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
            return bidNotif
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21
            if numCardsIHave >= 4:
                # We have a fit in diamonds
                ts.fitSuit = Suit.DIAMOND
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(Suit.DIAMOND, FitState.SUPPORT)
                bidNotif = BidNotif(4, Suit.DIAMOND, ts)
                return bidNotif
            else:
                ts.setSuitState(Suit.DIAMOND, FitState.NO_SUPPORT)            
            # Do I have 6+ clubs?
            if player.hand.getNumCardsInSuit(Suit.CLUB) >= 6:
                ts.candidateSuit = Suit.CLUB
                bidNotif = BidNotif(4, Suit.CLUB, ts)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
        print("openRebid_1C_1D: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1Mi_1Ma")
    def openRebid_1Mi_1Ma(self, table, player):
        Log.write("openRebid_1Mi_1Ma by %s\n" % player.pos.name)
        ts = player.teamState        
        # How many points do I have?
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        openingSuit = player.teamState.candidateSuit
        numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)
        
        # How many cards do I have in partner's suit
        partnerSuit = player.teamState.bidSeq[-1][1]
        (numCardsIHave, numHighCards) = player.hand.evalSuitStrength(partnerSuit)
        numSpades = 0
        if partnerSuit == Suit.HEART:
            numSpades = player.hand.getNumCardsInSuit(Suit.SPADE)

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            if numCardsIHave >= 4:
                # We have a fit in partner's major
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(2, partnerSuit, ts)
                return bidNotif
            else:
                ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
            if numSpades >= 4:
                ts.candidateSuit = Suit.SPADE
                bidNotif = BidNotif(1, Suit.SPADE, ts)
                return bidNotif
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(2, openingSuit, ts)
                return bidNotif
            if player.teamState.competition:
                ts.candidateSuit = Suit.ALL
                ts.force = Force.PASS
                bidNotif = BidNotif(0, Suit.ALL, ts)
                return bidNotif
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
            return bidNotif

        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            if numCardsIHave >= 4:
                # We have a fit in partner's major
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(3, partnerSuit, ts)
                return bidNotif
            else:
                ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
            
            if player.hand.isHandBalanced():
                if hcPts >= 18:
                    ts.candidateSuit = Suit.ALL
                    bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
                    return bidNotif
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(3, openingSuit, ts)
                return bidNotif
            if numSpades >= 4:
                ts.candidateSuit = Suit.SPADE
                bidNotif = BidNotif(2, Suit.SPADE, ts)
                return bidNotif
            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 4:
                    ts.candidateSuit = Suit.CLUB
                    bidNotif = BidNotif(2, Suit.CLUB, ts)
                    return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
            return bidNotif
        
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            if numCardsIHave >= 4:
                # We have a fit in partner's major
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(4, partnerSuit, ts)
                return bidNotif
            if player.hand.isHandBalanced():
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                return bidNotif
            if numCardsInSuit >= 6:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
                return bidNotif
            if numSpades >= 4:
                ts.candidateSuit = Suit.SPADES
                bidNotif = BidNotif(3, Suit.SPADES)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
        print("openRebid_1Mi_1Ma: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1H_1S")
    def openRebid_1H_1S(self, table, player):
        Log.write("openRebid_1H_1S by %s\n" % player.pos.name)
        ts = player.teamState     

        # How many points do I have?
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        # How many cards do I have in partner's suit
        partnerSuit = player.teamState.bidSeq[-1][1]
        (numCardsIHave, numHighCards) = player.hand.evalSuitStrength(partnerSuit)
        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            if numCardsIHave >= 4:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(2, partnerSuit, ts)
                return bidNotif
            if player.hand.isHandBalanced():
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
                return bidNotif
            
            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(2, openingSuit, ts)
                return bidNotif

            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
            return bidNotif

        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            if numCardsIHave >= 4:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(3, partnerSuit, ts)
                return bidNotif

            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(3, openingSuit, ts)
                return bidNotif
            if player.hand.isHandBalanced() and totalPts == 18:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
            return bidNotif
        
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            if numCardsIHave >= 4:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(4, partnerSuit, ts)
                return bidNotif
            
            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(4, openingSuit, ts)
                return bidNotif

            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
        print("openRebid_1H_1S: ERROR - should not reach here")

        
    @OpenerFunctions.register(command="openRebid_1Mi_1NT")
    def openRebid_1Mi_1NT(self, table, player):
        Log.write("openRebid_1Mi_1NT by %s\n" % player.pos.name)
        ts = player.teamState        

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            if player.hand.isHandBalanced():
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(0, Suit.ALL, ts)
                return bidNotif

            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 4:
                    ts.candidateSuit = Suit.CLUB
                    bidNotif = BidNotif(2, Suit.CLUB, ts)
                    return bidNotif
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.DIAMOND)
                if numCardsInSuit >= 6:
                    ts.candidateSuit = Suit.DIAMOND
                    bidNotif = BidNotif(2, Suit.DIAMOND, ts)
                    return bidNotif
            elif openingSuit == Suit.CLUB:
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 5:
                    ts.candidateSuit = Suit.CLUB
                    bidNotif = BidNotif(2, Suit.CLUB, ts)
                    return bidNotif
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
            
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            if player.hand.isHandBalanced():
                return (2, Suit.NOTRUMP)
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(2, suitA, ts)
                return bidNotif
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(2, suitA, ts)
                return bidNotif
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(2, suitB, ts)
                return bidNotif
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(2, suitB, ts)
                return bidNotif
            
            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.DIAMOND)
                if numCardsInSuit >= 6:
                    ts.candidateSuit = Suit.DIAMOND
                    bidNotif = BidNotif(3, Suit.DIAMOND, ts)
                    return bidNotif
            elif openingSuit == Suit.CLUB:
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 5:
                    ts.candidateSuit = Suit.CLUB
                    bidNotif = BidNotif(3, Suit.CLUB, ts)
                    return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
            return bidNotif
        
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            if player.hand.isHandBalanced():
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                return bidNotif
            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.DIAMOND)
                if numCardsInSuit >= 6:
                    ts.candidateSuit = Suit.DIAMOND
                    bidNotif = BidNotif(4, Suit.DIAMOND, ts)
                    return bidNotif
            elif openingSuit == Suit.CLUB:
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 5:
                    ts.candidateSuit = Suit.CLUB
                    bidNotif = BidNotif(4, Suit.CLUB, ts)
                    return bidNotif

            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
        print("openRebid_1Mi_1NT: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_1Mi_nMi")
    def openRebid_1Mi_nMi(self, table, player):
        Log.write("openRebid_1Mi_nMi by %s\n" % player.pos.name)
        ts = player.teamState        

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]
        if partnerLevel < 2 or partnerLevel > 3:
            print("openRebid: 1Mi_nMi: ERROR-partner level %d" % partnerLevel)    
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
        
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18
            # Inverted minors
            if partnerLevel == 2:
                bidNotif = BidNotif(3, openingSuit, ts)
                return bidNotif
            elif partnerLevel == 3:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
                return bidNotif
            
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            # Inverted minors
            if partnerLevel == 2:
                if player.hand.hasStoppers():
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                    return bidNotif
                if totalPts == 21:
                    ts.candidateSuit = openingSuit
                    bidNotif = BidNotif(4, openingSuit, ts)
                    return bidNotif
                else:
                    ts.candidateSuit = openingSuit
                    bidNotif = BidNotif(3, openingSuit, ts)
                    return bidNotif
            elif partnerLevel == 3:
                if player.hand.hasStoppers():
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                    return bidNotif
                else:
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
                    return bidNotif
        print("openRebid_1Mi_nMi: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1Ma_nMa")
    def openRebid_1Ma_nMa(self, table, player):
        Log.write("openRebid_1Ma_nMa by %s\n" % player.pos.name)
        ts = player.teamState        

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]
        if partnerLevel < 2 or partnerLevel > 4:
            print("openRebid: 1Ma_nMa: ERROR-partner level %d" % partnerLevel)
            
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if partnerLevel == 4:
            ts.candidateSuit = Suit.ALL
            ts.force = Force.PASS
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
        if partnerLevel == 3:
            if totalPts >= 13 and totalPts <= 14:
                ts.myMinPoints = 13
                ts.myMaxPoints = 15        
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(0, Suit.ALL, ts)
                return bidNotif
            if totalPts >= 15 and totalPts <= 19:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(4, openingSuit, ts)
                return bidNotif
            else:
                # Blackwood
                ts.fitSuit = openingSuit
                ts.candidateSuit = Suit.ALL
                ts.convention = Conv.BLACKWOOD
                bidNotif = BidNotif(4, Suit.NOTRUMP, ts)
                return bidNotif
        # Partner level = 2
        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
        if totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            ts.candidateSuit = Suit.ALL
            ts.fitSuit = openingSuit
            bidNotif = BidNotif(3, openingSuit, ts)
            return bidNotif
        if totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            ts.candidateSuit = Suit.ALL
            ts.fitSuit = openingSuit
            bidNotif = BidNotif(4, openingSuit, ts)
            return bidNotif
        print("openRebid_1Ma_nMa: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1Ma_1NT")
    def openRebid_1Ma_1NT(self, table, player):
        Log.write("openRebid_1Ma_1NT by %s\n" % player.pos.name)
        ts = player.teamState        

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(2, openingSuit, ts)
                return bidNotif
            numMinor = player.hand.getNumCardsInSuit(Suit.DIAMOND)
            if numMinor >= 4:
                ts.candidateSuit = Suit.DIAMOND
                bidNotif = BidNotif(2, Suit.DIAMOND, ts)
                return bidNotif
            numMinor = player.hand.getNumCardsInSuit(Suit.CLUB)
            if numMinor >= 3:
                ts.candidateSuit = Suit.CLUB
                bidNotif = BidNotif(2, Suit.CLUB, ts)
                return bidNotif

            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(2, suitA, ts)
                return bidNotif
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(2, suitA, ts)
                return bidNotif
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(2, suitB, ts)
                return bidNotif
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(2, suitB, ts)
                return bidNotif
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
        
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(3, openingSuit, ts)
                return bidNotif
            numMinor = player.hand.getNumCardsInSuit(Suit.DIAMOND)
            if numMinor >= 4:
                ts.candidateSuit = Suit.DIAMOND
                bidNotif = BidNotif(3, Suit.DIAMOND, ts)
                return bidNotif
            numMinor = player.hand.getNumCardsInSuit(Suit.CLUB)
            if numMinor >= 3:
                ts.candidateSuit = Suit.CLUB
                bidNotif = BidNotif(3, Suit.CLUB, ts)
                return bidNotif

            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(2, Suit.NOTRUMP, ts)
            return bidNotif
        
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            if suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
            if suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
            if numCardsInSuit >= 6 and player.hand.hasStoppers():
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                return bidNotif
            if hcPts >= 18 and hcPts <= 19 and player.hand.isHandBalanced():
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                return bidNotif
            if numCardsInSuit >= 7:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(4, openingSuit, ts)
                return bidNotif
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(3, openingSuit, ts)
                return bidNotif

            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
        print("openRebid_1Ma_1NT: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_1Ma_4W")
    def openRebid_1Ma_4W(self, table, player):
        Log.write("openRebid_1Ma_4W by %s\n" % player.pos.name)
        ts = player.teamState        
        # Splinter
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]
        
        if totalPts >= 13 and totalPts <= 16:
            ts.myMinPoints = 13
            ts.myMaxPoints = 16        
            ts.candidateSuit = openingSuit
            if openingSuit == Suit.HEART and partnerSuit == Suit.SPADE:
                bidNotif = BidNotif(5, openingSuit, ts)
            else:
                bidNotif = BidNotif(4, openingSuit, ts)
            return bidNotif
        # Explore slam with Blackwood
        ts.myMinPoints = 17
        ts.myMaxPoints = 21        
        bidNotif = BidNotif(4, Suit.NOTRUMP, ts)
        return bidNotif
    
    @OpenerFunctions.register(command="openRebid_1Mi_nNT")
    def openRebid_1Mi_nNT(self, table, player):
        Log.write("openRebid_1Mi_nNT by %s\n" % player.pos.name)
        ts = player.teamState

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]
        if partnerLevel < 2 or partnerLevel > 3:
            print("openRebid: 1Mi_nNT: ERROR-partner level %d" % partnerLevel)
        if partnerLevel == 3:
            # Gerber
            ts.fitSuit = Suit.NOTRUMP
            ts.setSuitState(Suit.NOTRUMP, FitState.PLAY)
            ts.candidateSuit = Suit.ALL
            ts.force = Force.GAME
            ts.convention = Conv.GERBER
            bidNotif = BidNotif(4, Suit.CLUB, ts)
            return bidNotif
        
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)

        if totalPts <= 17:
            ts.myMinPoints = 13
            ts.myMaxPoints = 17
            if player.hand.isHandBalanced():
                ts.fitSuit = Suit.NOTRUMP
                ts.setSuitState(Suit.NOTRUMP, FitState.PLAY)
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                return bidNotif
            if openingSuit == Suit.DIAMOND and numCardsInSuit >= 6:
                ts.candidateSuit = Suit.DIAMOND
                bidNotif = BidNotif(3, Suit.DIAMOND, ts)
                return bidNotif
            if openingSuit == Suit.CLUB and numCardsInSuit >= 5:
                ts.candidateSuit = Suit.CLUB
                bidNotif = BidNotif(3, Suit.CLUB, ts)
                return bidNotif
            ts.fitSuit = Suit.NOTRUMP
            ts.setSuitState(Suit.NOTRUMP, FitState.PLAY)
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
            
        elif totalPts >= 18 and totalPts <= 21:
            # Gerber
            ts.fitSuit = Suit.NOTRUMP
            ts.setSuitState(Suit.NOTRUMP, FitState.PLAY)
            ts.candidateSuit = Suit.ALL
            ts.force = Force.GAME
            ts.convention = Conv.GERBER
            bidNotif = BidNotif(4, Suit.CLUB, ts)
            return bidNotif
        print("openRebid_1Mi_nNT: ERROR - should not reach here")

    # Jacoby 2NT    
    @OpenerFunctions.register(command="openRebid_1Ma_2NT")
    def openRebid_1Ma_2NT(self, table, player):
        Log.write("openRebid_1Ma_2NT by %s\n" % player.pos.name)
        ts = player.teamState        

        # Do I have a singleton or void?
        openingSuit = player.teamState.candidateSuit
        singleSuit = player.hand.hasSingletonOrVoid(openingSuit)
        if singleSuit != Suit.ALL:
            ts.convention = Conv.CUE_BID
            bidNotif = BidNotif(3, singleSuit, ts)
            return bidNotif
        
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            ts.candidateSuit = openingSuit
            bidNotif = BidNotif(4, openingSuit, ts)
            return bidNotif
        
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
            
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 4:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(4, suitA, ts)
                return bidNotif
            elif suitB != openingSuit and isMinor(suitB) and numCardsB >= 4:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(4, suitB, ts)
                return bidNotif
            else:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(3, openingSuit, ts)
                return bidNotif
        print("openRebid_1Ma_2NT: ERROR - should not reach here")

        
    @OpenerFunctions.register(command="openRebid_1Ma_3NT")
    def openRebid_1Ma_3NT(self, table, player):
        Log.write("openRebid_1Ma_3NT by %s\n" % player.pos.name)
        ts = player.teamState        

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts >= 13 and totalPts <= 14:
            ts.myMinPoints = 13
            ts.myMaxPoints = 14
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif

        # Explore slam with Gerber
        ts.myMinPoints = 15
        ts.myMaxPoints = 21
        ts.fitSuit = Suit.NOTRUMP
        ts.setSuitState(Suit.NOTRUMP, FitState.PLAY)
        ts.candidateSuit = Suit.ALL
        ts.convention = Conv.GERBER
        bidNotif = BidNotif(4, Suit.CLUB, ts)
        return bidNotif
        print("openRebid_1Ma_3NT: ERROR - should not reach here")
        
        
    @OpenerFunctions.register(command="openRebid_2_over_1")
    def openRebid_2_over_1(self, table, player):
        Log.write("openRebid_2_over_1 by %s\n" % player.pos.name)
        ts = player.teamState        

        openingSuit = player.teamState.candidateSuit
        
        # What suit did my partner bid?
        partnerSuit = ts.bidSeq[-1][1]
        if partnerSuit.value > openingSuit[0]:
            print("2_over_1: ERROR-partner did not bid under opening suit")
        numCardsPartnersSuit = player.hand.getNumCardsInSuit(partnerSuit)
        if numCardsPartnersSuit >= 4:
            ts.setSuitState(partnerSuit, FitState.SUPPORT)
        else:
            ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
            
        # How many points do I have?
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(2, openingSuit, ts)
                return bidNotif
            if ts.suitState[partnerSuit] == FitState.SUPPORT:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(3, partnerSuit, ts)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
        
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(3, openingSuit, ts)
                return bidNotif
            if ts.suitState[partnerSuit] == FitState.SUPPORT:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(4, partnerSuit, ts)
                return bidNotif
            # No support for partner's suit
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif

        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            # Bid jump shift
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and suitA != partnerSuit:
                if suitA.level > partnerSuit.level:
                    ts.candidateSuit = suitA
                    bidNotif = BidNotif(partnerSuit.level + 1, suitA, ts)
                    return bidNotif
                else:
                    ts.candidateSuit = suitA
                    bidNotif = BidNotif(partnerSuit.level + 2, suitA, ts)
                    return bidNotif
                    return (partnerSuit.level + 2, suitA)
            if suitB != openingSuit and suitB != partnerSuit:
                if suitB.level > partnerSuit.level:
                    ts.candidateSuit = suitB
                    bidNotif = BidNotif(partnerSuit.level + 1, suitB, ts)
                    return bidNotif
                else:
                    ts.candidateSuit = suitB
                    bidNotif = BidNotif(partnerSuit.level + 2, suitB, ts)
                    return bidNotif
        print("openRebid_2_over_1: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_1NT_Pass")
    def openRebid_1NT_Pass(self, table, player):
        Log.write("openRebid_1NT_Pass by %s\n" % player.pos.name)
        ts = player.teamState
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif

    @OpenerFunctions.register(command="openRebid_1NT_2C")
    def openRebid_1NT_2C(self, table, player):
        Log.write("openRebid_1NT_2C by %s\n" % player.pos.name)
        ts = player.teamState        
        # Stayman
        numHearts = player.hand.getNumCardsInSuit(Suit.HEART)
        numSpades = player.hand.getNumCardsInSuit(Suit.SPADE)

        if numHearts < 4 and numSpades < 4:
            ts.candidateSuit = Suit.DIAMOND
            bidNotif = BidNotif(2, Suit.DIAMOND, ts)
            return bidNotif
        if numHearts == 4 and numSpades == 4:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(2, Suit.HEART, ts)
            return bidNotif
        if numHearts == 5 and numSpades == 5:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(2, Suit.SPADE, ts)
            return bidNotif
        if numHearts > numSpades:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(2, Suit.HEART, ts)
            return bidNotif
        else:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(2, Suit.SPADE, ts)
            return bidNotif
        print("openRebid_1NT_2C: ERROR - should not reach here")
    
    @OpenerFunctions.register(command="openRebid_1NT_2W")
    def openRebid_1NT_2W(self, table, player):
        Log.write("openRebid_1NT_2W by %s\n" % player.pos.name)
        ts = player.teamState        

        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many points do I have?
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
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
            numCardsInSuit = player.hand.getNumCardsInSuit(bidSuit)
            if numCardsInSuit >= 4:
                bidLevel += 1

        ts.candidateSuit = bidSuit
        bidNotif = BidNotif(bidLevel, bidSuit, ts)
        return bidNotif
        print("openRebid_1NT_2W: ERROR - should not reach here")


    @OpenerFunctions.register(command="openRebid_1NT_nNT")
    def openRebid_1NT_nNT(self, table, player):
        Log.write("openRebid_1NT_nNT by %s\n" % player.pos.name)
        ts = player.teamState        

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        
        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]

        if partnerLevel == 2:
            if hcPts > 15:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                return bidNotif
            else:
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(0, Suit.ALL, ts)
                return bidNotif
        elif partnerLevel == 3:
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
        elif partnerLevel == 4:
            if hcPts > 15:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
                return bidNotif
            else:
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(0, Suit.ALL, ts)
                return bidNotif
        elif partnerLevel == 5:
            # Gerber
            ts.convention = Conv.GERBER
            ts.candidateSuit = Suit.CLUB
            bidNotif = BidNotif(6, Suit.CLUB, ts)
            return bidNotif
        else:
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
           
    @OpenerFunctions.register(command="openRebid_1NT_3Mi")
    def openRebid_1NT_3Mi(self, table, player):
        Log.write("openRebid_1NT_3Mi by %s\n" % player.pos.name)
        ts = player.teamState
        
        # What suit did my partner bid? Partner promises 5 cards.
        partnerSuit = ts.bidSeq[-1][1]
        numCardsPartnersSuit = player.hand.getNumCardsInSuit(partnerSuit)
        if numCardsPartnersSuit >= 3:
            ts.setSuitState(partnerSuit, FitState.SUPPORT)
        else:
            ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
        
        numHearts = player.hand.getNumCardsInSuit(Suit.HEART)
        numSpades = player.hand.getNumCardsInSuit(Suit.SPADE)

        if numHearts < 4 and numSpades < 4:
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
        if numHearts == 4 and numSpades == 4:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(3, Suit.HEART, ts)
            return bidNotif
        if numHearts == 5 and numSpades == 5:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(3, Suit.SPADE, ts)
            return bidNotif
        if numHearts > numSpades:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(3, Suit.HEART, ts)
            return bidNotif
        else:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(3, Suit.SPADE, ts)
            return bidNotif
        print("openRebid_1NT_3Mi: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1NT_3Ma")
    def openRebid_1NT_3Ma(self, table, player):
        Log.write("openRebid_1NT_3Ma by %s\n" % player.pos.name)
        ts = player.teamState        
        
        # What suit did my partner bid? Partner promises 5 cards.
        partnerSuit = ts.bidSeq[-1][1]
        numCardsPartnersSuit = player.hand.getNumCardsInSuit(partnerSuit)
        if numCardsPartnersSuit >= 3:
            ts.setSuitState(partnerSuit, FitState.SUPPORT)
        else:
            ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)

        if partnerSuit == Suit.SPADE:
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(1, Suit.NOTRUMP, ts)
            return bidNotif

        # Partner's suit is HEART
        if ts.suitState[partnerSuit] == FitState.SUPPORT:
            ts.fitSuit = partnerSuit
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(4, partnerSuit, ts)
            return bidNotif
        
        ts.candidateSuit = Suit.NOTRUMP
        bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
        return bidNotif
                    
    @OpenerFunctions.register(command="openRebid_1NT_4Ma")
    def openRebid_1NT_4Ma(self, table, player):
        Log.write("openRebid_1NT_4Ma by %s\n" % player.pos.name)
        ts = player.teamState        

        # What suit did my partner bid? Partner promises 6 cards.
        partnerSuit = ts.bidSeq[-1][1]
        numCardsPartnersSuit = player.hand.getNumCardsInSuit(partnerSuit)
        if numCardsPartnersSuit >= 2:
            ts.setSuitState(partnerSuit, FitState.SUPPORT)
        else:
            ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)

        # Not enough for slam
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif

    @OpenerFunctions.register(command="openRebid_2C_2D")
    def openRebid_2C_2D(self, table, player):
        Log.write("openRebid_2C_2D by %s\n" % player.pos.name)
        ts = player.teamState        

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        
        if isMajor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(2, suitA, ts)
                return bidNotif
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                ts.candidateSuit = suitA
                bidNotif = BidNotif(2, suitB, ts)
                return bidNotif
        if isMinor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            elif numCardsA == numCardsB:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
        print("openRebid_2C_2D: ERROR - should not reach here")


    @OpenerFunctions.register(command="openRebid_2C_2Ma")
    def openRebid_2C_2Ma(self, table, player):
        Log.write("openRebid_2C_2Ma by %s\n" % player.pos.name)
        ts = player.teamState        

        # What suit did my partner bid? Partner promises 5 cards.
        partnerSuit = ts.bidSeq[-1][1]
        numCardsPartnersSuit = player.hand.getNumCardsInSuit(partnerSuit)
        if numCardsPartnersSuit >= 3:
            ts.setSuitState(partnerSuit, FitState.SUPPORT)
        else:
            ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)

        if ts.suitState[partnerSuit] == FitState.SUPPORT:
            ts.fitSuit = partnerSuit
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(3, partnerSuit, ts)
            return bidNotif
        
        # Find best suit to bid
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if isMajor(suitA):
            ts.candidateSuit = suitA
            if suitA.level < partnerSuit.level:
                bidNotif = BidNotif(partnerSuit.level, suitA, ts)
                return bidNotif
            else:
                bidNotif = BidNotif(partnerSuit.level + 1, suitA, ts)
                return bidNotif
        # My best suit is a minor. Bid them up the line
        if numCardsA == numCardsB:
            ts.candidateSuit = suitB
            bidNotif = BidNotif(3, suitB, ts)
            return bidNotif
        else:
            ts.candidateSuit = suitA
            bidNotif = BidNotif(3, suitA, ts)
            return bidNotif
        print("openRebid_2C_2Ma: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_2C_2NT")
    def openRebid_2C_2NT(self, table, player):
        Log.write("openRebid_2C_2NT by %s\n" % player.pos.name)
        ts = player.teamState        

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        
        if isMajor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
        if isMinor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            elif numCardsA == numCardsB:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
        print("openRebid_2C_2NT: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_2C_3Mi")
    def openRebid_2C_3Mi(self, table, player):
        Log.write("openRebid_2C_3Mi by %s\n" % player.pos.name)
        ts = player.teamState        

        # What suit did my partner bid? Partner promised 5 cards.
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many cards do I have in partner's suit
        numCardsPartnersSuit = player.hand.getNumCardsInSuit(partnerSuit)

        if numCardsPartnersSuit >= 3:
            ts.setSuitState(partnerSuit, FitState.SUPPORT)
        else:
            ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)

        if ts.suitState[partnerSuit] == FitState.SUPPORT:
            ts.fitSuit = partnerSuit
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(4, partnerSuit, ts)
            return bidNotif
        
        # Find best suit to bid
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if isMajor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                ts.candidateSuit = suitB
                bidNotif = BidNotif(3, suitB, ts)
                return bidNotif
            else:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(3, suitA, ts)
                return bidNotif    
        if suitB.isMajor():
            ts.candidateSuit = suitB
            bidNotif = BidNotif(3, suitB, ts)
            return bidNotif
        if suitA == Suit.DIAMOND:
           if partnerSuit == Suit.CLUB:
               ts.candidateSuit = suitA
               bidNotif = BidNotif(3, suitA, ts)
               return bidNotif
        if suitA == Suit.CLUB:
           if partnerSuit == Suit.DIAMOND:
               ts.candidateSuit = suitA
               bidNotif = BidNotif(4, suitA, ts)
               return bidNotif
        if suitB == Suit.DIAMOND:
           if partnerSuit == Suit.CLUB:
               ts.candidateSuit = suitB
               bidNotif = BidNotif(3, suitb, ts)
               return bidNotif
        if suitB == Suit.CLUB:
           if partnerSuit == Suit.DIAMOND:
               ts.candidateSuit = suitB
               bidNotif = BidNotif(4, suitB, ts)
               return bidNotif
        print("openRebid_2C_3Mi: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_weak_Pass")
    def openRebid_weak_Pass(self, table, player):
        Log.write("openRebid_weak_Pass by %s\n" % player.pos.name)
        ts = player.teamState
        ts.force = Force.PASS
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif
        
    @OpenerFunctions.register(command="openRebid_2weak_2W")
    def openRebid_2weak_2W(self, table, player):
        Log.write("openRebid_2weak_2W by %s\n" % player.pos.name)
        ts = player.teamState        
        
        openingSuit = player.teamState.candidateSuit

        # What suit did my partner bid? Partner promises 5+ cards.
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many cards do I have in partner's suit
        numCardsInSuit = player.hand.getNumCardsInSuit(partnerSuit)

        if numCardsInSuit >= 3:
            ts.fitSuit = partnerSuit
            ts.candidateSuit = Suit.ALL
            # How many points do I have?
            (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
            totalPts = hcPts + distPts
            if totalPts < 10:
                bidNotif = BidNotif(3, partnerSuit, ts)
            else:
                bidNotif = BidNotif(4, partnerSuit, ts)
            return bidNotif
                
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif
        print("openRebid_2weak_2W: ERROR - should not reach here")


    @OpenerFunctions.register(command="openRebid_2weak_2NT")
    def openRebid_2weak_2NT(self, table, player):
        Log.write("openRebid_2weak_2NT by %s\n" % player.pos.name)
        ts = player.teamState        

        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        
        if totalPts >= 10 and player.hand.hasStoppers():
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(3, Suit.NOTRUMP, ts)
            return bidNotif
        ts.candidateSuit = openingSuit
        bidNotif = BidNotif(3, openingSuit, ts)
        return bidNotif
        print("openRebid_2weak_2NT: ERROR - should not reach here")

        
    @OpenerFunctions.register(command="openRebid_2weak_3")
    def openRebid_2weak_3(self, table, player):
        Log.write("openRebid_2weak_3 by %s\n" % player.pos.name)
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif

    
    @OpenerFunctions.register(command="openRebid_2weak_3NT")
    def openRebid_weak_3NT(self, table, player):
        Log.write("openRebid_2weak_3NT by %s\n" % player.pos.name)
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif
        

    @OpenerFunctions.register(command="openRebid_2NT_3C")
    def openRebid_2NT_3C(self, table, player):
        Log.write("openRebid_2NT_3C by %s\n" % player.pos.name)
        ts = player.teamState        
        # Stayman
        numHearts = player.hand.getNumCardsInSuit(Suit.HEART)
        numSpades = player.hand.getNumCardsInSuit(Suit.SPADE)

        if numHearts < 4 and numSpades < 4:
            ts.candidateSuit = Suit.DIAMOND
            bidNotif = BidNotif(3, Suit.DIAMOND, ts)
            return bidNotif
        if numHearts == 4 and numSpades == 4:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(3, Suit.HEART, ts)
            return bidNotif
        if numHearts == 5 and numSpades == 5:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(3, Suit.SPADE, ts)
            return bidNotif
        if numHearts > numSpades:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(3, Suit.HEART, ts)
            return bidNotif
        else:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(3, Suit.SPADE, ts)
            return bidNotif
        print("openRebid_1NT_3C: ERROR - should not reach here")
    
    @OpenerFunctions.register(command="openRebid_2NT_3W")
    def openRebid_2NT_3W(self, table, player):
        Log.write("openRebid_2NT_3W by %s\n" % player.pos.name)
        ts = player.teamState        
        
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

        ts.candidateSuit = bidSuit
        bidNotif = BidNotif(bidLevel, bidSuit, ts)
        return bidNotif
    
    @OpenerFunctions.register(command="openRebid_2NT_3NT")
    def openRebid_2NT_3NT(self, table, player):
        Log.write("openRebid_2NT_3NT by %s\n" % player.pos.name)
        ts = player.teamState
        ts.force = Force.PASS
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif

    @OpenerFunctions.register(command="openRebid_2NT_nNT")
    def openRebid_2NT_nNT(self, table, player):
        Log.write("openRebid_2NT_nNT by %s\n" % player.pos.name)
        ts = player.teamState        
        ts.fitSuit = Suit.NOTRUMP
        
        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]

        if partnerLevel == 5:
            # Gerber
            ts.candidateSuit = Suit.CLUB
            bidNotif = BidNotif(6, Suit.CLUB, ts)
            return bidNotif
        else:
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
        
    @OpenerFunctions.register(command="openRebid_3weak_3W")
    def openRebid_3weak_3W(self, table, player):
        Log.write("openRebid_3weak_3W by %s\n" % player.pos.name)
        ts = player.teamState        

        openingSuit = player.teamState.candidateSuit
        
        # What suit did my partner bid?
        partnerSuit = player.teamState.bidSeq[-1][1]

        # How many cards do I have in partner's suit
        numCardsInSuit = player.hand.getNumCardsInSuit(partnerSuit)

        if numCardsInSuit >= 2:
            if isMajor(partnerSuit):
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(4, partnerSuit, ts)
                return bidNotif
            
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif
        print("openRebid_3weak_3W: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_3_4")
    def openRebid_3_4(self, table, player):
        Log.write("openRebid_3_4 by %s\n" % player.pos.name)
        ts = player.teamState
        ts.force = Force.PASS
        return (0, Suit.ALL)
        
    @OpenerFunctions.register(command="openRebid_3NT_nNT")
    def openRebid_3NT_nNT(self, table, player):
        Log.write("openRebid_3NT_nNT by %s\n" % player.pos.name)
        ts = player.teamState

        # What level did my partner bid?
        partnerLevel = player.teamState.bidSeq[-1][0]

        if partnerLevel == 4:
            # Gerber
            ts.candidateSuit = Suit.CLUB
            bidNotif = BidNotif(5, Suit.CLUB, ts)
            return bidNotif
        elif partnerLevel == 5:
            ts.fitSuit = Suit.NOTRUMP
            ts.candidateSuit = Suit.ALL
            ts.force = Force.PASS
            bidNotif = BidNotif(6, Suit.NOTRUMP, ts)
            return bidNotif
        else:
            ts.fitSuit = Suit.NOTRUMP
            ts.candidateSuit = Suit.ALL
            ts.force = Force.PASS
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
