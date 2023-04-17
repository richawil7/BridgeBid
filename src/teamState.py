'''
A class to represent the state of the collective hand of the
partnership.
Each player will have an instance of this class, as it indicates
that player's view.
'''

import json
from infoLog import Log
from enums import *
from openBid import *


class TeamState:

    def __init__(self):
        self.fitSuit = Suit.ALL        # updated by bid node
        self.candidateSuit = Suit.ALL  # updated by bid node/handler
        self.myMinPoints = 0           # updated by bid node/handler
        self.myMaxPoints = 0           # updated by bid node/handler
        self.convention = Conv.NATURAL # updated by notif handler
        self.force = Force.NONE        # updated by bid node/handler
        self.competition = False       # updated by notif handler
        self.bidSeq = []               # bidder: bid, non-bidder: notif
        self.suitState = {Suit.NOTRUMP: FitState.UNKNOWN, Suit.SPADE: FitState.UNKNOWN, Suit.HEART: FitState.UNKNOWN, Suit.DIAMOND: FitState.UNKNOWN, Suit.CLUB: FitState.UNKNOWN}
        
        self.gameState = GameState.UNKNOWN # updated by bid node/handler
        self.partnerMinPoints = 0      # updated by notification handler
        self.partnerMaxPoints = 0      # updated by notification handler
        self.partnerNumAces = 0        # updated by notification handler
        self.partnerNumKings = 0       # updated by notification handler
        self.teamMinPoints = 0         # updated by notification handler
        self.teamMaxPoints = 0         # updated by notification handler

    def show(self):
        bidSeqStr = ''        
        for bid in self.bidSeq:
            bidStr = getBidStr(bid[0], bid[1])
            bidSeqStr += bidStr + "-"
        Log.write("Team state for bid sequence %s\n" % bidSeqStr)
        Log.write("\tFit suit:\t\t%s\n" % self.fitSuit.name)
        Log.write("\tCandidate suit:\t%s\n" % self.candidateSuit.name)
        for suit, fit in self.suitState.items():
            Log.write("\t\t%s:\t%s\n" % (suit.name, fit.name))
            
        Log.write("\tConvention: %s\n" % self.convention.name)
        Log.write("\tForce type: %s\n" % self.force.name)
        
        Log.write("\tMy min points = %d\n" % self.myMinPoints)
        Log.write("\tMy max points = %d\n" % self.myMaxPoints)
        Log.write("\tPartner min points = %d\n" % self.partnerMinPoints)
        Log.write("\tPartner max points = %d\n" % self.partnerMaxPoints)
        Log.write("\tTeam min points = %d\n" % self.teamMinPoints)
        Log.write("\tTeam max points = %d\n" % self.teamMaxPoints)
        Log.write("\tGame state: %s\n" % self.gameState.name)

    # Merge the information from a bidding tree node into the team state
    def mergeTreeNode(self, player, bidTreeNode, playerRole):
        self.convention = bidTreeNode.convention
        self.force = bidTreeNode.force
        if playerRole == PlayerRole.RESPONDER:
            self.myMinPoints = bidTreeNode.responderMinPoints
            self.myMaxPoints = bidTreeNode.responderMaxPoints
            (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
            # My partner is the opener
            self.partnerMinPoints = bidTreeNode.openerMinPoints
            self.partnerMaxPoints = bidTreeNode.openerMaxPoints
        else:
            # I am the opener, or the would-be opener
            self.myMinPoints = bidTreeNode.openerMinPoints
            self.myMaxPoints = bidTreeNode.openerMaxPoints
            (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_LONG)
            # My partner is the responder
            self.partnerMinPoints = bidTreeNode.responderMinPoints
            self.partnerMaxPoints = bidTreeNode.responderMaxPoints

        totalPts = hcPts + distPts 
        self.teamMinPoints = self.partnerMinPoints + totalPts
        self.teamMaxPoints = self.partnerMaxPoints + totalPts

        
    def addTeamBid(self, level, suit):
        self.bidSeq.append((level, suit))

    def setSuitState(self, suit, fit):
        self.suitState[suit] = fit
