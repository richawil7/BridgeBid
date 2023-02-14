'''
A class to represent the state of the collective hand of the
partnership.
Each player will have an instance of this class, as it indicates
that player's view.
'''

import json
from enums import *
from openBid import *


class TeamState:

    def __init__(self):
        self.partnerMinPoints = 0
        self.partnerMaxPoints = 0
        self.teamMinPoints = 0
        self.teamMaxPoints = 0
        self.bidSeq = []
        
    def show(self):
        print("Partner min points = %d" % self.partnerMinPoints)
        print("Partner max points = %d" % self.partnerMaxPoints)
        print("Team min points = %d" % self.teamMinPoints)
        print("Team max points = %d" % self.teamMaxPoints)
        for bid in self.bidSeq:
            print("Bid level %d suit %s" % (bid.level, bid.suit.name))

    # Merge the information from a bidding tree node into the team state
    def mergeTreeNode(self, player, bidTreeNode, playerRole):
        if playerRole == PlayerRole.RESPONDER:
            (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
            # My partner is the opener
            self.partnerMinPoints = bidTreeNode.openerMinPoints
            self.partnerMaxPoints = bidTreeNode.openerMaxPoints
        else:
            # I am the opener, or the would-be opener
            (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_LONG)
            # My partner is the responder
            self.partnerMinPoints = bidTreeNode.responderMinPoints
            self.partnerMaxPoints = bidTreeNode.responderMaxPoints

        totalPts = hcPts + distPts 
        self.teamMinPoints = self.partnerMinPoints + totalPts
        self.teamMaxPoints = self.partnerMaxPoints + totalPts

        
    def addTeamBid(self, level, suit):
        self.bidSeq.append((level, suit))

        
    # Returns the callable nextState and hint function for the current hand state
    def analyzeHandState(self, table, player, roundNum):
        if roundNum == 1:
            (calcBidFx, hintFx) = analyzeRound1(table, player)
            return (calcBidFx, hintFx)
        elif roundNum == 2:
            (calcBidFx, hintFx) = analyzeRound2(table, player)
            return (calcBidFx, hintFx)
        else:
            (calcBidFx, hintFx) = analyzeRound3Plus(table, player)
            return (calcBidFx, hintFx)

    def analyzeRound1(self, table, hasOpener, competition, roundNum, bidsList, hand):
        # Get state of the table
        hasOpener = table.hasOpener
        competition = table.competition
        roundNum = table.roundNum
        bidsList = table.bidsList

        # Check if I can open
        iCanOpen = canIOpen(self.hand, competition, player.seat) 
        if iCanOpen:
            hintFx = getHintForOpener
            caclBidFx = calcOpenBid
        else:
            hintFx = getHintForOpener
            caclBidFx = caclPassBid
        
        # Determine this player's bidding state
        if not hasOpener and not competition:
            # No one has opened yet
            if iCanOpen:
                player.teamRole = TeamRole.OFFENSE
                player.playerRole = PlayerRole.OPENER
                return (calcOpenBid, getHintForOpener)

        elif not hasOpener and competition:
            print("bridgePlayer: computerBidReq: Error-invalid state ")

        elif hasOpener:
            # Check if my partner was the opener
            if len(bidsList) >= 2:
                if self.seat >= 3:
                    partnerBidIdx = self.seat - 2 - 1
                else:
                    partnerBidIdx = 4 + self.seat - 2 - 1
                partnerBid = bidsList[partnerBidIdx][0]
                if partnerBid > 0:
                    # My partner opened
                    if roundNum == 1:
                        writeLog(table, "handState: analyzeR1: partner opened\n")
                    self.teamRole = TeamRole.OFFENSE
                    self.playerRole = PlayerRole.RESPONDER
                    (calcBidFx, hintFx) = analyzeResponder(table)
                    return (calcBidFx, hintFx)
                else:
                    # My partner passed
                    writeLog(self.table, "bridgePlayer: compBidReq: partner passed\n")
                    if iCanOpen:
                        self.teamRole = TeamRole.OFFENSE
                        self.playerRole = PlayerRole.OPENER
                        return (calcOpenBid, getHintForOpener)
            else:
                if iCanOpen:
                    self.teamRole = TeamRole.OFFENSE
                    self.playerRole = PlayerRole.OPENER
                    return (calcOpenBid, getHintForOpener)

        return (calcBidFx, hintFx)
