'''
A class that describes a bid that was made.
It is generated by the bidder and sent to all the players (including
the bidder) for processing.
'''

from infoLog import Log
from enums import *

class BidNotif:

    def __init__(self, bidLevel, bidSuit, teamState):
        teamState.bidSeq.append((bidLevel, bidSuit))
        self.bid = (bidLevel, bidSuit)
        self.minPoints = teamState.myMinPoints
        self.maxPoints = teamState.myMaxPoints
        self.convention = teamState.convention
        self.force = teamState.force
        self.suitState = teamState.suitState.copy()
        self.gameState = teamState.gameState

    def processBlackwoodResponse(self):
        print("processBlackwoodResponse")
        if self.bid[0] == 5:
            if self.bid[1] == Suit.CLUB:
                self.partnerNumAces = 4
            elif self.bid[1] == Suit.DIAMOND:
                self.partnerNumAces = 1
            elif self.bid[1] == Suit.HEART:
                self.partnerNumAces = 2
            elif self.bid[1] == Suit.SPADE:
                self.partnerNumAces = 3
        elif self.bid[0] == 6:
            if self.bid[1] == Suit.CLUB:
                self.partnerNumKings = 4
            elif self.bid[1] == Suit.DIAMOND:
                self.partnerNumKings = 1
            elif self.bid[1] == Suit.HEART:
                self.partnerNumKings = 2
            elif self.bid[1] == Suit.SPADE:
                self.partnerNumKings = 3

    def processGerberResponse(self):
        print("processBlackwoodResponse")
        if self.bid[0] == 4:
            if self.bid[1] == Suit.DIAMOND:
                self.partnerNumAces = 4
            elif self.bid[1] == Suit.HEART:
                self.partnerNumAces = 1
            elif self.bid[1] == Suit.SPADE:
                self.partnerNumAces = 2
            elif self.bid[1] == Suit.NOTRUMP:
                self.partnerNumAces = 3
        elif self.bid[0] == 5:
            if self.bid[1] == Suit.DIAMOND:
                self.partnerNumKings = 4
            elif self.bid[1] == Suit.HEART:
                self.partnerNumKings = 1
            elif self.bid[1] == Suit.SPADE:
                self.partnerNumKings = 2
            elif self.bid[1] == Suit.NOTRUMP:
                self.partnerNumKings = 3

    def processCuebidResponse(self):
        print("processCuebidResponse")

        
    def notifHandler(self, player):
        print("notifHandler for player %s" % player.pos.name)
        teamState = player.teamState

        # We don't want to process a notification if a bid node exists
        numTeamBids = len(teamState.bidSeq)
        if numTeamBids <= 2:
            bidSeqStr = ''        
            for bid in self.bidSeq:
                bidStr = getBidStr(bid[0], bid[1])
                bidSeqStr += bidStr + "-"
            print("notifHandler: ignoring notif for bid seq %s" % bidSeqStr)
            return
        
        # Merge this notification into a team state
        # Update fit suit
        for (suit, fitState) in self.suitState.items():
            if teamState.suitState[suit] == FitState.UNKNOWN:
                teamState.suitState[suit] = fitState
            if teamState.fitSuit == Suit.ALL and fitState == FitState.PLAY:
                teamState.fitSuit = suit

        # Candidate suit depends upon fit state
        if self.suitState[self.bid[1]] == FitState.UNKNOWN and self.convention == Conv.NATURAL:
            teamState.candidateSuit = self.bid[1]
            
        teamState.partnerMinPoints = self.minPoints
        teamState.partnerMaxPoints = self.maxPoints

        if player.playerRole == PlayerRole.OPENER:
            distMethod = DistMethod.HCP_LONG
        elif player.playerRole == PlayerRole.RESPONDER:
            distMethod = DistMethod.HCP_SHORT
        else:    
            distMethod = DistMethod.HCP_LONG
        (myHcPts, myDistPts) = player.hand.evalHand(distMethod)
        myTotalPts = myHcPts + myDistPts
        teamState.teamMinPoints = teamState.partnerMinPoints + myTotalPts
        teamState.teamMaxPoints = teamState.partnerMaxPoints + myTotalPts
        
        teamState.convention = self.convention
        if self.convention == Conv.BLACKWOOD:
            self.processBlackwoodResponse()
        elif self.convention == Conv.GERBER:
            self.processGerberResponse()
        elif self.convention == Conv.CUE_BID:
            self.processCuebidResponse()
                    
        teamState.force = teamState.force
        
        teamState.bidSeq.append(self.bid)
        if player.playerRole == PlayerRole.OPENER:
            # The opener copies the game state from the notification
            if self.gameState.value > teamState.gameState.value:
                teamState.gameState = self.gameState
        elif player.playerRole == PlayerRole.RESPONDER:
            # The responder sets the game state
            if teamState.fitSuit == Suit.ALL:
                teamState.gameState == GameState.UNKNOWN
            else:
                if teamState.fitSuit.isMinor():
                    minGamePts = 29
                else: 
                    minGamePts = 26
                if teamState.teamMinPts < minGamePts:
                    teamState.gameState = GameState.PARTSCORE
                elif teamState.teamMinPts < 33:
                    teamState.gameState = GameState.GAME
                elif teamState.teamMinPts < 36:
                    teamState.gameState = GameState.SMALL_SLAM
                else:
                    teamState.gameState = GameState.LARGE_SLAM
                
                        
    
