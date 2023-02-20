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
        bidSeqStr = ''        
        for bid in self.bidSeq:
            bidStr = getBidStr(bid[0], bid[1])
            bidSeqStr += bidStr + "-"
        print("Team bid sequence: %s", bidSeqStr)

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

