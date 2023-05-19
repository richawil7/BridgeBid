'''
Functions used for generating bids by the opener after getting
a responding bid from the partner
'''

from infoLog import Log
from enums import Suit, Level, DistMethod, FitState, Force, GameState, Conv
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
        
        # Create a bid notification
        bidNotif = BidNotif(player, bidLevel, bidSuit, Conv.NATURAL, Force.PASS)
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
                bidNotif = BidNotif(player, 1, secondSuit)
                return bidNotif
            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                bidNotif = BidNotif(player, 2, openingSuit)
                return bidNotif          
            if player.teamState.competition:
                bidNotif = BidNotif(player, 0, Suit.ALL)
                return bidNotif                
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
            return bidNotif                
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18
            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                bidNotif = BidNotif(player, 3, openingSuit)
                return bidNotif                
            if secondSuit != Suit.ALL:
                ts.candidateSuit = secondSuit
                bidNotif = BidNotif(player, 1, secondSuit)
                return bidNotif                
            bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
            return bidNotif                
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21
            if isMinor(suitB) and numCardsB >= 5 or isMajor(suitB) and numCardsB >= 4:
                # Bid a jump shift of second suit
                if suitB.level > openingSuit.level:
                    ts.candidateSuit = secondSuit
                    bidNotif = BidNotif(player, 2, secondSuit)
                    return bidNotif                
                else:
                    ts.candidateSuit = secondSuit
                    bidNotif = BidNotif(player, 3, secondSuit)
                    return bidNotif                

            if player.hand.getNumCardsInSuit(openingSuit) >= 6:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
                return bidNotif                

            if player.hand.isHandBalanced():
                if hcPts >= 20:
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
                    return bidNotif                
                if hcPts >= 18:
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
                    return bidNotif                
            else:
                if player.hand.getNumCardsInSuit(openingSuit) >= 7:
                    # Bid game
                    if isMajor(openingSuit):
                        bidNotif = BidNotif(player, 4, openingSuit)
                        return bidNotif                
                    else:
                        bidNotif = BidNotif(player, 5, openingSuit)
                        return bidNotif                
                elif player.hand.getNumCardsInSuit(openingSuit) >= 6:
                    bidNotif = BidNotif(player, 3, openingSuit)
                    return bidNotif                
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
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
                bidNotif = BidNotif(player, 2, Suit.DIAMOND)
                return bidNotif
            else:
                ts.setSuitState(Suit.DIAMOND, FitState.NO_SUPPORT)
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
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
                bidNotif = BidNotif(player, 3, Suit.DIAMOND)
                return bidNotif
            else:
                ts.setSuitState(Suit.DIAMOND, FitState.NO_SUPPORT)
            # Do I have 6+ clubs?
            if player.hand.getNumCardsInSuit(Suit.CLUB) >= 6:
                ts.candidateSuit = Suit.CLUB
                bidNotif = BidNotif(player, 3, Suit.CLUB)
                return bidNotif
            if totalPts == 18:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
            return bidNotif
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21
            if numCardsIHave >= 4:
                # We have a fit in diamonds
                ts.fitSuit = Suit.DIAMOND
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(Suit.DIAMOND, FitState.SUPPORT)
                bidNotif = BidNotif(player, 4, Suit.DIAMOND)
                return bidNotif
            else:
                ts.setSuitState(Suit.DIAMOND, FitState.NO_SUPPORT)            
            # Do I have 6+ clubs?
            if player.hand.getNumCardsInSuit(Suit.CLUB) >= 6:
                ts.candidateSuit = Suit.CLUB
                bidNotif = BidNotif(player, 4, Suit.CLUB)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
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
                bidNotif = BidNotif(player, 2, partnerSuit)
                return bidNotif
            else:
                ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
            if numSpades >= 4:
                ts.candidateSuit = Suit.SPADE
                bidNotif = BidNotif(player, 1, Suit.SPADE)
                return bidNotif
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 2, openingSuit)
                return bidNotif
            if player.teamState.competition:
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(player, 0, Suit.ALL, Conv.NATURAL, Force.PASS)
                return bidNotif
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
            return bidNotif

        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            if numCardsIHave >= 4:
                # We have a fit in partner's major
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(player, 3, partnerSuit)
                return bidNotif
            else:
                ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
            
            if player.hand.isHandBalanced():
                if hcPts >= 18:
                    ts.candidateSuit = Suit.ALL
                    bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
                    return bidNotif
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 3, openingSuit)
                return bidNotif
            if numSpades >= 4:
                ts.candidateSuit = Suit.SPADE
                bidNotif = BidNotif(player, 2, Suit.SPADE)
                return bidNotif
            if openingSuit == Suit.DIAMOND:
                numCardsInSuit = player.hand.getNumCardsInSuit(Suit.CLUB)
                if numCardsInSuit >= 4:
                    ts.candidateSuit = Suit.CLUB
                    bidNotif = BidNotif(player, 2, Suit.CLUB)
                    return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
            return bidNotif
        
        elif totalPts >= 19:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            if numCardsIHave >= 4:
                # We have a fit in partner's major
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(player, 4, partnerSuit)
                return bidNotif
            if player.hand.isHandBalanced():
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
                return bidNotif
            if numCardsInSuit >= 6:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
                return bidNotif
            if numSpades >= 4:
                ts.candidateSuit = Suit.SPADE
                bidNotif = BidNotif(player, 3, Suit.SPADE)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
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
                bidNotif = BidNotif(player, 2, partnerSuit)
                return bidNotif
            if player.hand.isHandBalanced():
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
                return bidNotif
            
            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 2, openingSuit)
                return bidNotif

            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
            return bidNotif

        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            if numCardsIHave >= 4:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(player, 3, partnerSuit)
                return bidNotif

            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 3, openingSuit)
                return bidNotif
            if player.hand.isHandBalanced() and totalPts == 18:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
                return bidNotif
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
            return bidNotif
        
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            if numCardsIHave >= 4:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                bidNotif = BidNotif(player, 4, partnerSuit)
                return bidNotif
            
            openingSuit = player.teamState.candidateSuit
            numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 4, openingSuit)
                return bidNotif

            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
            return bidNotif
        print("openRebid_1H_1S: ERROR - should not reach here")

        
    @OpenerFunctions.register(command="openRebid_1Mi_1NT")
    def openRebid_1Mi_1NT(self, table, player):
        Log.write("openRebid_1Mi_1NT by %s\n" % player.pos.name)
        ts = player.teamState        
        ts.convention = Conv.NATURAL
        
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)

        # In two over one, a 1 NT bid from responder is forcing for one round
        # Find another bid, leaning towards showing a 4 card major
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if suitA != openingSuit and isMajor(suitA) and numCardsA >= 4:
            ts.candidateSuit = suitA
        elif suitB != openingSuit and isMajor(suitB) and numCardsB >= 4:
            ts.candidateSuit = suitB
        elif openingSuit == Suit.DIAMOND and numCardsInSuit >= 6:
            ts.candidateSuit = Suit.DIAMOND
        elif openingSuit == Suit.CLUB and numCardsInSuit >= 5:
            ts.candidateSuit = Suit.CLUB
        elif suitA != openingSuit and isMinor(suitA) and numCardsA >= 5:
            ts.candidateSuit = suitA
        elif suitB != openingSuit and isMinor(suitB) and numCardsB >= 5:
            ts.candidateSuit = suitB
        else:
            ts.candidateSuit = Suit.NOTRUMP

        # We have a suit to bid, now calculate the bid level
        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            bidLevel = 2
            
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18
            bidLevel = 2
            if openingSuit == Suit.DIAMOND and numCardsInSuit >= 6:
                bidLevel = 3
            elif openingSuit == Suit.CLUB and numCardsInSuit >= 5:
                bidLevel = 3
        
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21
            if player.hand.isHandBalanced():
                ts.candidateSuit = Suit.NOTRUMP
                bidLevel = 3
            elif openingSuit == Suit.DIAMOND and numCardsInSuit >= 6:
                bidLevel = 4
            elif openingSuit == Suit.CLUB and numCardsInSuit >= 5:
                bidLevel = 4
            else:
                bidLevel = 3
        bidNotif = BidNotif(player, bidLevel, ts.candidateSuit)
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
            bidNotif = BidNotif(player, 0, Suit.ALL)
            return bidNotif
        
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18
            # Inverted minors
            if partnerLevel == 2:
                bidNotif = BidNotif(player, 3, openingSuit)
                return bidNotif
            elif partnerLevel == 3:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
                return bidNotif
            
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            # Inverted minors
            if partnerLevel == 2:
                if player.hand.hasStoppers():
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
                    return bidNotif
                if totalPts == 21:
                    ts.candidateSuit = openingSuit
                    bidNotif = BidNotif(player, 4, openingSuit)
                    return bidNotif
                else:
                    ts.candidateSuit = openingSuit
                    bidNotif = BidNotif(player, 3, openingSuit)
                    return bidNotif
            elif partnerLevel == 3:
                if player.hand.hasStoppers():
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
                    return bidNotif
                else:
                    ts.candidateSuit = Suit.NOTRUMP
                    bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
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
            bidNotif = BidNotif(player, 0, Suit.ALL, Conv.NATURAL, Force.PASS)
            return bidNotif
        if partnerLevel == 3:
            if totalPts >= 13 and totalPts <= 14:
                ts.myMinPoints = 13
                ts.myMaxPoints = 15        
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(player, 0, Suit.ALL)
                return bidNotif
            if totalPts >= 15 and totalPts <= 19:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 4, openingSuit)
                return bidNotif
            else:
                # Blackwood
                ts.fitSuit = openingSuit
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(player, 4, Suit.NOTRUMP, Conv.BLACKWOOD_REQ, Force.ONE_ROUND)
                return bidNotif
        # Partner level = 2
        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(player, 0, Suit.ALL)
            return bidNotif
        if totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            ts.candidateSuit = Suit.ALL
            ts.fitSuit = openingSuit
            bidNotif = BidNotif(player, 3, openingSuit)
            return bidNotif
        if totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            ts.candidateSuit = Suit.ALL
            ts.fitSuit = openingSuit
            bidNotif = BidNotif(player, 4, openingSuit)
            return bidNotif
        print("openRebid_1Ma_nMa: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_1Ma_1NT")
    def openRebid_1Ma_1NT(self, table, player):
        Log.write("openRebid_1Ma_1NT by %s\n" % player.pos.name)
        ts = player.teamState        
        ts.convention = Conv.NATURAL

        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)

        # In two over one, a 1NT response is forcing for one round
        # Find a suit to bid
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        
        if numCardsInSuit >= 6:
            ts.candidateSuit = openingSuit
        elif openingSuit == Suit.HEART and player.hand.getNumCardsInSuit(Suit.SPADE >= 4):
            ts.candidateSuit = Suit.SPADE
        elif suitB != openingSuit and numCardsB >= 4:
            ts.candidateSuit = suitB
        else:
            ts.candidateSuit = Suit.NOTRUMP
            
        # We have a suit to bid, now find the bid level
        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15
            bidLevel = 2
        
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18
            bidLevel = 3
            if ts.candidateSuit == Suit.NOTRUMP:
                bidLevel = 2
        
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21
            bidLevel = 3
            if hcPts >= 18 and hcPts <= 19 and player.hand.isHandBalanced():
                ts.candidateSuit = Suit.NOTRUMP
            elif numCardsInSuit >= 7:
                bidLevel = 4

            bidNotif = BidNotif(player, bidLevel, ts.candidateSuit)
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
            ts.gameState = GameState.Game
            if openingSuit == Suit.HEART and partnerSuit == Suit.SPADE:
                bidNotif = BidNotif(player, 5, openingSuit)
            else:
                bidNotif = BidNotif(player, 4, openingSuit)
            return bidNotif
        # Explore slam with Blackwood
        ts.myMinPoints = 17
        ts.myMaxPoints = 21        
        ts.gameState = GameState.SMALL_SLAM     
        bidNotif = BidNotif(player, 4, Suit.NOTRUMP, Conv.BLACKWOOD_REQ, Force.ONE_ROUND)
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
            ts.setSuitState(Suit.NOTRUMP, FitState.SUPPORT)
            ts.candidateSuit = Suit.ALL
            ts.gameState = GameState.GAME
            bidNotif = BidNotif(player, 4, Suit.CLUB, Conv.GERBER_REQ, Force.ONE_ROUND)
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
                ts.setSuitState(Suit.NOTRUMP, FitState.SUPPORT)
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
                return bidNotif
            if openingSuit == Suit.DIAMOND and numCardsInSuit >= 6:
                ts.candidateSuit = Suit.DIAMOND
                bidNotif = BidNotif(player, 3, Suit.DIAMOND)
                return bidNotif
            if openingSuit == Suit.CLUB and numCardsInSuit >= 5:
                ts.candidateSuit = Suit.CLUB
                bidNotif = BidNotif(player, 3, Suit.CLUB)
                return bidNotif
            ts.fitSuit = Suit.NOTRUMP
            ts.setSuitState(Suit.NOTRUMP, FitState.SUPPORT)
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
            return bidNotif
            
        elif totalPts >= 18 and totalPts <= 21:
            # Gerber
            ts.fitSuit = Suit.NOTRUMP
            ts.setSuitState(Suit.NOTRUMP, FitState.SUPPORT)
            ts.candidateSuit = Suit.ALL
            ts.gameState = GameState.GAME
            bidNotif = BidNotif(player, 4, Suit.CLUB, Conv.GERBER_REQ, Force.ONE_ROUND)
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
            bidNotif = BidNotif(player, 3, singleSuit, Conv.CUE_BID, Force.ONE_ROUND)
            return bidNotif
        
        # How many points do I have?
        openingSuit = player.teamState.candidateSuit
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            ts.candidateSuit = openingSuit
            bidNotif = BidNotif(player, 4, openingSuit)
            return bidNotif
        
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
            return bidNotif
            
        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
            if suitA != openingSuit and isMinor(suitA) and numCardsA >= 4:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(player, 4, suitA)
                return bidNotif
            elif suitB != openingSuit and isMinor(suitB) and numCardsB >= 4:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(player, 4, suitB)
                return bidNotif
            else:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 3, openingSuit)
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
            bidNotif = BidNotif(player, 0, Suit.ALL)
            return bidNotif

        # Explore slam with Gerber
        ts.myMinPoints = 15
        ts.myMaxPoints = 21
        ts.fitSuit = Suit.NOTRUMP
        ts.setSuitState(Suit.NOTRUMP, FitState.SUPPORT)
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 4, Suit.CLUB, Conv.GERBER_REQ, Force.ONE_ROUND)
        return bidNotif
        print("openRebid_1Ma_3NT: ERROR - should not reach here")
        
        
    @OpenerFunctions.register(command="openRebid_2_over_1")
    def openRebid_2_over_1(self, table, player):
        Log.write("openRebid_2_over_1 by %s\n" % player.pos.name)
        ts = player.teamState
        # Clear the convention
        ts.convention = Conv.NATURAL
        openingSuit = player.teamState.candidateSuit
        
        # What suit did my partner bid?
        partnerSuit = ts.bidSeq[-1][1]
        if partnerSuit.value <= openingSuit.value:
            print("2_over_1: ERROR-partner did not bid under opening suit")
        # How many cards is partner promising with their bid?
        numCardsPartnersSuit = player.hand.getNumCardsInSuit(partnerSuit)
        if partnerSuit == Suit.HEART:
            # Responder promises 5
            if numCardsPartnersSuit >= 3:
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                ts.fitSuit = partnerSuit
            else:
                ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
        elif partnerSuit == Suit.DIAMOND:
            # Responder promises 4
            if numCardsPartnersSuit >= 4:
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                ts.fitSuit = partnerSuit
            else:
                ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
        elif partnerSuit == Suit.CLUB and openingSuit != Suit.DIAMOND: 
            # Responder promises 4
            if numCardsPartnersSuit >= 4:
                ts.setSuitState(partnerSuit, FitState.SUPPORT)
                ts.fitSuit = partnerSuit
            else:
                ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
        # A 1D-2C bid does not promise any number of clubs
        
        # How many points do I have?
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        numCardsInSuit = player.hand.getNumCardsInSuit(openingSuit)
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()

        if totalPts <= 15:
            ts.myMinPoints = 13
            ts.myMaxPoints = 15        
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 2, openingSuit)
                return bidNotif
            if ts.suitState[partnerSuit] == FitState.SUPPORT:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(player, 3, partnerSuit)
                return bidNotif
            # Can I show a 4+ card major
            if isMajor(suitB):
                ts.candidateSuit = suitB
                bidNotif = BidNotif(player, 2, suitB)
                return bidNotif
            # Default     
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 2, Suit.NOTRUMP)
            return bidNotif
        
        elif totalPts >= 16 and totalPts <= 18:
            ts.myMinPoints = 16
            ts.myMaxPoints = 18        
            if numCardsInSuit >= 6:
                ts.candidateSuit = openingSuit
                bidNotif = BidNotif(player, 3, openingSuit)
                return bidNotif
            if ts.suitState[partnerSuit] == FitState.SUPPORT:
                ts.fitSuit = partnerSuit
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(player, 4, partnerSuit)
                return bidNotif
            # Can I show a 4+ card major
            if isMajor(suitB):
                ts.candidateSuit = suitB
                bidNotif = BidNotif(player, 3, suitB)
                return bidNotif
            # Default
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
            return bidNotif

        elif totalPts >= 19 and totalPts <= 21:
            ts.myMinPoints = 19
            ts.myMaxPoints = 21        
            if numCardsA >= 6:
                # Rebid opening suit at 3 level
                ts.candidateSuit = suitA
                bidNotif = BidNotif(player, 3, suitA)
                return bidNotif

            # Otherwise bid my second best suit as a jump shift
            if suitB != partnerSuit:
                if suitB.value > partnerSuit.value:
                    ts.candidateSuit = suitB
                    bidNotif = BidNotif(player, partnerSuit.value + 1, suitB)
                    return bidNotif
                else:
                    ts.candidateSuit = suitB
                    bidNotif = BidNotif(player, partnerSuit.value + 2, suitB)
                    return bidNotif
            else:
                # Jump to show large hand
                ts.candidateSuit = suitB
                bidNotif = BidNotif(player, 4, suitB)
                return bidNotif
        print("openRebid_2_over_1: ERROR - should not reach here")
        
    @OpenerFunctions.register(command="openRebid_1NT_Pass")
    def openRebid_1NT_Pass(self, table, player):
        Log.write("openRebid_1NT_Pass by %s\n" % player.pos.name)
        ts = player.teamState
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 0, Suit.ALL)
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
            bidNotif = BidNotif(player, 2, Suit.DIAMOND, Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        if numHearts == 4 and numSpades == 4:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(player, 2, Suit.HEART, Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        if numHearts == 5 and numSpades == 5:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(player, 2, Suit.SPADE, Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        if numHearts > numSpades:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(player, 2, Suit.HEART, ts,Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        else:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(player, 2, Suit.SPADE, Conv.STAYMAN_RSP, Force.ONE_ROUND)
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

        # Jacoby transfer response
        if partnerSuit == Suit.DIAMOND:
            bidSuit = Suit.HEART
            bidLevel = 2
            numCardsInSuit = player.hand.getNumCardsInSuit(Suit.HEART)
            if numCardsInSuit >= 3:
                ts.suitState[Suit.HEART] = FitState.SUPPORT
                ts.fitSuit = Suit.HEART
            else:
                ts.suitState[Suit.HEART] = FitState.NO_SUPPORT
        elif partnerSuit == Suit.HEART:
            bidSuit = Suit.SPADE
            bidLevel = 2
            numCardsInSuit = player.hand.getNumCardsInSuit(Suit.SPADE)
            if numCardsInSuit >= 3:
                ts.suitState[Suit.SPADE] = FitState.SUPPORT
                ts.fitSuit = Suit.SPADE
            else:
                ts.suitState[Suit.SPADE] = FitState.NO_SUPPORT
        elif partnerSuit == Suit.SPADE:
            bidSuit = Suit.CLUB
            bidLevel = 3
            numCardsInSuit = player.hand.getNumCardsInSuit(Suit.CLUB)
            if numCardsInSuit >= 3:
                ts.suitState[Suit.CLUB] = FitState.SUPPORT
                ts.fitSuit = Suit.CLUB
            else:
                ts.suitState[Suit.CLUB] = FitState.NO_SUPPORT
        else:
            print("openerRebid_1NT_2W: ERROR-called with 2C response")

        if totalPts >= 17 and bidSuit != Suit.CLUB:
            numCardsInSuit = player.hand.getNumCardsInSuit(bidSuit)
            if numCardsInSuit >= 4:
                bidLevel += 1

        ts.candidateSuit = bidSuit
        bidNotif = BidNotif(player, bidLevel, bidSuit, Conv.JACOBY_XFER_RSP, Force.NONE)
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
                bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
                return bidNotif
            else:
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(player, 0, Suit.ALL)
                return bidNotif
        elif partnerLevel == 3:
            ts.candidateSuit = Suit.ALL
            ts.gameState = GameState.GAME
            bidNotif = BidNotif(player, 0, Suit.ALL)
            return bidNotif
        elif partnerLevel == 4:
            if hcPts > 15:
                ts.candidateSuit = Suit.NOTRUMP
                bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
                return bidNotif
            else:
                ts.candidateSuit = Suit.ALL
                bidNotif = BidNotif(player, 0, Suit.ALL)
                return bidNotif
        elif partnerLevel == 5:
            # Gerber
            ts.candidateSuit = Suit.CLUB
            bidNotif = BidNotif(player, 6, Suit.CLUB)
            bidNotif.convention = Conv.GERBER
            return bidNotif
        elif partnerLevel == 6:
            ts.candidateSuit = Suit.ALL
            ts.gameState = GameState.SMALL_SLAM
            bidNotif = BidNotif(player, 0, Suit.ALL)
            return bidNotif
        else:
            ts.candidateSuit = Suit.ALL
            ts.gameState = GameState.LARGE_SLAM
            bidNotif = BidNotif(player, 0, Suit.ALL)
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
            ts.fitSuit = partnerSuit
        else:
            ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)
        
        numHearts = player.hand.getNumCardsInSuit(Suit.HEART)
        numSpades = player.hand.getNumCardsInSuit(Suit.SPADE)

        if numHearts < 4 and numSpades < 4:
            ts.candidateSuit = Suit.NOTRUMP
            bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
            return bidNotif
        if numHearts == 4 and numSpades == 4:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(player, 3, Suit.HEART)
            return bidNotif
        if numHearts == 5 and numSpades == 5:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(player, 3, Suit.SPADE)
            return bidNotif
        if numHearts > numSpades:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(player, 3, Suit.HEART)
            return bidNotif
        else:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(player, 3, Suit.SPADE)
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
            bidNotif = BidNotif(player, 1, Suit.NOTRUMP)
            return bidNotif

        # Partner's suit is HEART
        if ts.suitState[partnerSuit] == FitState.SUPPORT:
            ts.fitSuit = partnerSuit
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(player, 4, partnerSuit)
            return bidNotif
        
        ts.candidateSuit = Suit.NOTRUMP
        bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
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
            ts.fitSuit = partnerSuit
        else:
            ts.setSuitState(partnerSuit, FitState.NO_SUPPORT)

        # Not enough for slam
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 0, Suit.ALL)
        return bidNotif

    @OpenerFunctions.register(command="openRebid_2C_2D")
    def openRebid_2C_2D(self, table, player):
        Log.write("openRebid_2C_2D by %s\n" % player.pos.name)
        ts = player.teamState        

        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        
        if isMajor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(player, 2, suitA)
                return bidNotif
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                ts.candidateSuit = suitA
                bidNotif = BidNotif(player, 2, suitB)
                return bidNotif
        if isMinor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(player, 3, suitA)
                return bidNotif
            elif numCardsA == numCardsB:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(player, 3, suitB)
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
            bidNotif = BidNotif(player, 3, partnerSuit)
            return bidNotif
        
        # Find best suit to bid
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if isMajor(suitA):
            ts.candidateSuit = suitA
            if suitA.level < partnerSuit.level:
                bidNotif = BidNotif(player, partnerSuit.level, suitA)
                return bidNotif
            else:
                bidNotif = BidNotif(player, partnerSuit.level + 1, suitA)
                return bidNotif
        # My best suit is a minor. Bid them up the line
        if numCardsA == numCardsB:
            ts.candidateSuit = suitB
            bidNotif = BidNotif(player, 3, suitB)
            return bidNotif
        else:
            ts.candidateSuit = suitA
            bidNotif = BidNotif(player, 3, suitA)
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
                bidNotif = BidNotif(player, 3, suitA)
                return bidNotif
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                ts.candidateSuit = suitB
                bidNotif = BidNotif(player, 3, suitB)
                return bidNotif
        if isMinor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(player, 3, suitA)
                return bidNotif
            elif numCardsA == numCardsB:
                ts.candidateSuit = suitB
                bidNotif = BidNotif(player, 3, suitB)
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
            bidNotif = BidNotif(player, 4, partnerSuit)
            return bidNotif
        
        # Find best suit to bid
        (suitA, numCardsA, suitB, numCardsB) = player.hand.numCardsInTwoLongestSuits()
        if isMajor(suitA):
            if numCardsA >= 5:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(player, 3, suitA)
                return bidNotif
            elif numCardsA == numCardsB:
                # 4 and 4 in the majors. Bid hearts
                ts.candidateSuit = suitB
                bidNotif = BidNotif(player, 3, suitB)
                return bidNotif
            else:
                ts.candidateSuit = suitA
                bidNotif = BidNotif(player, 3, suitA)
                return bidNotif    
        if isMajor(suitB):
            ts.candidateSuit = suitB
            bidNotif = BidNotif(player, 3, suitB)
            return bidNotif
        if suitA == Suit.DIAMOND:
           if partnerSuit == Suit.CLUB:
               ts.candidateSuit = suitA
               bidNotif = BidNotif(player, 3, suitA)
               return bidNotif
        if suitA == Suit.CLUB:
           if partnerSuit == Suit.DIAMOND:
               ts.candidateSuit = suitA
               bidNotif = BidNotif(player, 4, suitA)
               return bidNotif
        if suitB == Suit.DIAMOND:
           if partnerSuit == Suit.CLUB:
               ts.candidateSuit = suitB
               bidNotif = BidNotif(player, 3, suitb)
               return bidNotif
        if suitB == Suit.CLUB:
           if partnerSuit == Suit.DIAMOND:
               ts.candidateSuit = suitB
               bidNotif = BidNotif(player, 4, suitB)
               return bidNotif
        print("openRebid_2C_3Mi: ERROR - should not reach here")

    @OpenerFunctions.register(command="openRebid_weak_Pass")
    def openRebid_weak_Pass(self, table, player):
        Log.write("openRebid_weak_Pass by %s\n" % player.pos.name)
        ts = player.teamState
        ts.force = Force.PASS
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 0, Suit.ALL)
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
                bidNotif = BidNotif(player, 3, partnerSuit)
            else:
                bidNotif = BidNotif(player, 4, partnerSuit)
            return bidNotif
                
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 0, Suit.ALL)
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
            bidNotif = BidNotif(player, 3, Suit.NOTRUMP)
            return bidNotif
        ts.candidateSuit = openingSuit
        bidNotif = BidNotif(player, 3, openingSuit)
        return bidNotif
        print("openRebid_2weak_2NT: ERROR - should not reach here")

        
    @OpenerFunctions.register(command="openRebid_2weak_3")
    def openRebid_2weak_3(self, table, player):
        Log.write("openRebid_2weak_3 by %s\n" % player.pos.name)
        ts = player.teamState        
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 0, Suit.ALL)
        return bidNotif

    
    @OpenerFunctions.register(command="openRebid_2weak_3NT")
    def openRebid_weak_3NT(self, table, player):
        Log.write("openRebid_2weak_3NT by %s\n" % player.pos.name)
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 0, Suit.ALL)
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
            bidNotif = BidNotif(player, 3, Suit.DIAMOND, Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        if numHearts == 4 and numSpades == 4:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(player, 3, Suit.HEART, Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        if numHearts == 5 and numSpades == 5:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(player, 3, Suit.SPADE, Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        if numHearts > numSpades:
            ts.candidateSuit = Suit.HEART
            bidNotif = BidNotif(player, 3, Suit.HEART, Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        else:
            ts.candidateSuit = Suit.SPADE
            bidNotif = BidNotif(player, 3, Suit.SPADE, Conv.STAYMAN_RSP, Force.ONE_ROUND)
            return bidNotif
        print("openRebid_2NT_3C: ERROR - should not reach here")
    
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
            numCardsInSuit = player.hand.getNumCardsInSuit(Suit.HEART)
            if numCardsInSuit >= 3:
                ts.suitState[Suit.HEART] = FitState.SUPPORT
                ts.fitSuit = Suit.HEART
            else:
                ts.suitState[Suit.HEART] = FitState.NO_SUPPORT
            
        elif partnerSuit == Suit.HEART:
            bidSuit = Suit.SPADE
            bidLevel = 3
            numCardsInSuit = player.hand.getNumCardsInSuit(Suit.SPADE)
            if numCardsInSuit >= 3:
                ts.suitState[Suit.SPADE] = FitState.SUPPORT
                ts.fitSuit = Suit.SPADE
            else:
                ts.suitState[Suit.SPADE] = FitState.NO_SUPPORT
        else:
            print("openerRebid_2NT_3W: ERROR-called with 2C response")

        ts.candidateSuit = bidSuit
        bidNotif = BidNotif(player, bidLevel, bidSuit, Conv.JACOBY_XFER_RSP, Force.NONE)
        return bidNotif
    
    @OpenerFunctions.register(command="openRebid_2NT_3NT")
    def openRebid_2NT_3NT(self, table, player):
        Log.write("openRebid_2NT_3NT by %s\n" % player.pos.name)
        ts = player.teamState
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 0, Suit.ALL, Conv.NATURAL, Force.PASS)
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
            bidNotif = BidNotif(player, 6, Suit.CLUB)
            return bidNotif
        else:
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(player, 0, Suit.ALL)
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
                bidNotif = BidNotif(player, 4, partnerSuit)
                return bidNotif
            
        ts.candidateSuit = Suit.ALL
        bidNotif = BidNotif(player, 0, Suit.ALL)
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
            bidNotif = BidNotif(player, 5, Suit.CLUB)
            return bidNotif
        elif partnerLevel == 5:
            ts.fitSuit = Suit.NOTRUMP
            ts.candidateSuit = Suit.ALL
            bidNotif = BidNotif(player, 6, Suit.NOTRUMP, Conv.NATURAL, Force.PASS)
            return bidNotif
        else:
            ts.fitSuit = Suit.NOTRUMP
            ts.candidateSuit = Suit.ALL
            ts.force = Force.PASS
            bidNotif = BidNotif(player, 0, Suit.ALL)
            return bidNotif
