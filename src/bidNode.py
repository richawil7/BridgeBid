'''
A class to describe the state of the collective hand of a partnership.
Instances of this class are created by reading a json file from the 
bidding tree.
This class is similar to the teamState class.
Think of the bidNode as the static view of the partnership and is the same 
for both players. In contrast, each player has its own instance of the
teamState, and is that player's view.
'''

import json
from infoLog import Log
from enums import *
from bidUtils import *

bidTreeBaseDir = "/home/richawil/Documents/Programming/Apps/BridgeBid/bidding_trees"

# Return a bidNode instance from the bidding tree
def fetchBidTreeNode(bidSeq):
    # Build a pathname to the bid
    # If the first bid is a Pass, we need to strip it
    path = bidTreeBaseDir
    for i, bid in enumerate(bidSeq):
        if i == 0 and bid[0] == 0:
            # First bid was a Pass. Strip it unless it is the only bid.
            if len(bidSeq) > 1:
                # print("First bid was a Pass - ignoring")
                continue
            else:
                bidStr = "Pass"
        else:
            bidStr = getBidStr(bid[0], bid[1])
        path = path + '/' + bidStr
    path = path + '/' + 'bidNode.json'
    Log.write("fetchBidTreeNode %s\n" % path)
    
    # Open the file
    fh = open(path, 'r')
    bidDescriptor = json.load(fh)

    # Create an empty bid node
    bidNode = BidNode()
    for key in bidDescriptor.keys():
        #print("Key={} Value={}".format(key, bidDescriptor[key]))
        if key == "teamRole":
            bidNode.teamRole = TeamRole[bidDescriptor[key]]
        elif key == "fitSuit":
            bidNode.fitSuit = Suit[bidDescriptor[key]]
        elif key == "candidateSuit":
            bidNode.candidateSuit = Suit[bidDescriptor[key]]
        elif key == "convention":
            bidNode.convention = Conv[bidDescriptor[key]]
        elif key == "force":
            bidNode.force = Force[bidDescriptor[key]]
        elif key == "bidSeq":
            bidNode.bidSeq = bidDescriptor[key]
        elif key == "handler":
            bidNode.handler = bidDescriptor[key]
        elif key == "suitStates":
            for suitStr, fitStr in bidDescriptor[key].items():
                bidNode.suitState[Suit[suitStr]] = FitState[fitStr]
        elif key == "openerInfo":
            bidNode.openerMinPoints = bidDescriptor[key]["minPts"]
            bidNode.openerMaxPoints = bidDescriptor[key]["maxPts"]
            if bidDescriptor[key]["evalMethod"] == 'hcp-only':
                bidNode.openerEvalMethod = DistMethod.HCP_ONLY
            elif bidDescriptor[key]["evalMethod"] == 'hcp-short':
                bidNode.openerEvalMethod = DistMethod.HCP_SHORT
            elif bidDescriptor[key]["evalMethod"] == 'hcp-long':
                bidNode.openerEvalMethod = DistMethod.HCP_LONG
        elif key == "responderInfo":
            bidNode.responderMinPoints = bidDescriptor[key]["minPts"]
            bidNode.responderMaxPoints = bidDescriptor[key]["maxPts"]
            if bidDescriptor[key]["evalMethod"] == 'hcp-only':
                bidNode.responderEvalMethod = DistMethod.HCP_ONLY
            elif bidDescriptor[key]["evalMethod"] == 'hcp-short':
                bidNode.responderEvalMethod = DistMethod.HCP_SHORT
            elif bidDescriptor[key]["evalMethod"] == 'hcp-long':
                bidNode.responderEvalMethod = DistMethod.HCP_LONG
        elif key == "interpretation":
            bidNode.interpret = bidDescriptor[key]
        elif key == "hints":
            bidNode.bidHints.append(bidDescriptor['hints']['hint0'])
            bidNode.bidHints.append(bidDescriptor['hints']['hint1'])
            bidNode.bidHints.append(bidDescriptor['hints']['hint2'])                
    return bidNode
        
        
class BidNode:

    def __init__(self):
        # Static parameters derived from bidding tree node
        self.teamRole = TeamRole.UNKNOWN
        self.fitSuit = Suit.ALL
        self.candidateSuit = Suit.ALL
        self.convention = Conv.NATURAL
        self.openerMinPoints = 0
        self.openerMaxPoints = 0
        self.openerEvalMethod = DistMethod.HCP_ONLY
        self.responderMinPoints = 0
        self.responderMaxPoints = 0
        self.responderEvalMethod = DistMethod.HCP_ONLY
        self.suitState = {Suit.NOTRUMP: FitState.UNKNOWN, Suit.SPADE: FitState.UNKNOWN, Suit.HEART: FitState.UNKNOWN, Suit.DIAMOND: FitState.UNKNOWN, Suit.CLUB: FitState.UNKNOWN}
        self.force = Force.NONE
        self.nextBidder = PlayerRole.UNKNOWN
        self.handler = ""
        self.interpret = ""
        self.bidHints = []
        
    def show(self):
        print("Team role = %s" % self.teamRole.name)
        print("Fit suit = %s" % self.fitSuit.name)
        print("Candidate suit = %s" % self.candidateSuit.name)
        print("Suit states:")
        for suit, fitState in self.suitState:
            print("\t%s - %s" % (suit.name, fitState.name))
        print("Convention = %s" % self.convention.name)
        print("Force = %s" % self.force.name)
        print("Next Bidder = %s" % self.nextBidder.name)
        print("Handler name = %s" % self.handler)
        print("Opener min points = %d" % self.openerMinPoints)
        print("Opener max points = %d" % self.openerMaxPoints)
        print("Opener eval method = %s" % self.openerEvalMethod.name)
        print("Responder min points = %d" % self.responderMinPoints)
        print("Responder max points = %d" % self.responderMaxPoints)
        print("Responder eval method = %s" % self.responderEvalMethod.name)
        print("Interpretation = %s" % self.interpret)
        print("Hint 1 = %s" % self.bidHints[0])
        print("Hint 2 = %s" % self.bidHints[1])
        print("Hint 3 = %s" % self.bidHints[2])
