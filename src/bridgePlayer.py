'''
Bridge Player Class
A player of the game of Spades
'''

from infoLog import Log
from enums import Suit, Level, TeamRole, PlayerRole
from utils import *
from bidNode import *
from cardPile import CardPile
from teamState import TeamState
from player import Player
from bridgeHand import BridgeHand
from bidNotif import BidNotif
from bidUtils import *
from openBid import *
from responderBid import *
from nonNodeBid import *

class BridgePlayer(Player):

    def __init__(self, table, position, isHuman=False):
        super(BridgePlayer, self).__init__(table, position, isHuman)
        self.distribution = {Suit.SPADE : 0, Suit.HEART : 0, Suit.DIAMOND : 0, Suit.CLUB : 0}
        self.seat = 0
        self.playerRole = PlayerRole.UNKNOWN
        self.hand = BridgeHand(position)
        self.teamState = TeamState()
        self.lastNotif = None
        self.bidNode = BidNode()
        

    def startHand(self, leadPos):
        self.playerRole = PlayerRole.UNKNOWN
        # Calculate which seat I'm sitting in
        if self.pos.value >= leadPos.value:
            self.seat = self.pos.value - leadPos.value + 1
        else:
            self.seat = 4 + self.pos.value - leadPos.value + 1

        # Evaluate the hand and initialize the team state
        (hcPoints, distPoints) = self.hand.evalHand(DistMethod.HCP_LONG)

        # Initialize the team state
        self.teamState.__init__()
        self.teamState.minTeamPts = hcPoints
        self.teamState.maxTeamPts = hcPoints + distPoints
        numCards, longSuit = self.hand.findLongestSuit()
        self.teamState.candidateSuit = longSuit
        
    def bidRequest(self, table, listOfBids):
        if self.isHuman:
            curPos = table.currentPos
            player = table.players[curPos]
            # Ask the computer to calculate the bid for the human
            # But later it will be ignored
            player.computerBidRequest(table, table.hasOpener, player.teamState.competition, table.roundNum, table.bidsList, self.isHuman, player.hand)
            print("Use the dropdown boxes to enter a bid")
            
        # Thread will respond with a card played by computer
            

    '''
    Function to calculate a bid.
    Inputs:
        table - card table object
        hasOpener - boolean indicating if a player has already opened
        competition - boolean indicating if both teams have bid (other than pass)
        roundNum - number of the bidding round (starts at 1)
        bidsList - list of bids thus far
        hand - hand on which to perform the calculation (read-only)
    Returns:
        bid - the actual bid; a tuple of level and suit
    '''    
    def computerBidRequest(self, table, hasOpener, competition, roundNum, bidsList, isHuman, hand):
        if self.pos == TablePosition.NORTH or self.pos == TablePosition.SOUTH:
            Log.write("BidReq: pos={} hasOpener={} compet={} roundNum={}\n".format(self.pos.name, hasOpener, competition, roundNum))

        if roundNum == 1:
            bidNotif = self.bidRound1(table)

        elif roundNum == 2:
            bidNotif = self.bidRound2(table)

        elif roundNum >= 3:
            bidNotif = self.bidRound3(table)
        
        # Store this bid
        self.lastNotif = bidNotif
        (bidLevel, bidSuit) = (bidNotif.bid[0], bidNotif.bid[1])
        bidStr = getBidStr(bidLevel, bidSuit)
        if not isHuman:
            Log.write("BidRsp: %s bids %s\n" % (self.pos.name, bidStr))
            # Only submit the bid if the computer is this player
            self.table.bidResponse(self.pos, bidNotif)
        else:
            # This is the bid the computer thinks the human should make
            Log.write("BidRsp: Computer thinks human should bid %s\n" % bidStr)

        # Debug
        #if bidNotif.bid[0] != 0 or self.teamState.bidSeq[-1][0] != 0:    
        #    bidNotif.show()

        
    def bidRound1(self, table):
        # Figure out this player's bidding role
        self.playerRole = getMyPlayerRole(table, self)
        
        # Get the sequence of bids made by this partnership
        bidSeq = self.teamState.bidSeq
        
        # Fetch the bid node from the bidding tree for this bid sequence
        self.bidNode = fetchBidTreeNode(bidSeq)
  
        # Merge the bid tree node info into the team state
        self.teamState.mergeTreeNode(self, self.bidNode, self.playerRole)

        # FIX ME - debugging
        if self.pos == TablePosition.NORTH or self.pos == TablePosition.SOUTH:
            Log.write("Show team state for %s, prior to round 1 bid\n" % self.pos.name)
            self.teamState.show()
        
        if self.playerRole == PlayerRole.RESPONDER:
            # Call the handler function for the current team state
            bidNotif = table.responderRegistry.jump_table[self.bidNode.handler](table, self)
        else:
            # Call the handler function for the current team state
            bidNotif = table.openerRegistry.jump_table[self.bidNode.handler](table, self)

        # Update the bid notification using the bid node information
        newBidSeq = self.teamState.bidSeq.copy()
        newBidSeq.append(bidNotif.bid)
        nextBidNode = fetchBidTreeNode(newBidSeq)
        bidNotif.updateWithBidnode(self, nextBidNode)
        return bidNotif

        
    def bidRound2(self, table):
        # Get the sequence of bids made by this partnership
        bidSeq = self.teamState.bidSeq
        numBids = len(bidSeq)
        # Check if the first bid was a pass
        if bidSeq[0][0] == 0:
            # print("First bid was a pass")
            numBids -= 1
            
        # Figure out this player's bidding role
        if self.playerRole == PlayerRole.UNKNOWN:
            self.playerRole = getMyPlayerRole(table, self)

        if self.playerRole == PlayerRole.NONE:
            bidNotif = BidNotif(0, Suit.ALL, self.teamState)
            return bidNotif

        # FIX ME - debugging
        if self.pos == TablePosition.NORTH or self.pos == TablePosition.SOUTH:
            Log.write("Show team state for %s, prior to round 2 bid\n" % self.pos.name)
            self.teamState.show()
            
        if self.playerRole == PlayerRole.OPENER:
            # Fetch the bid node from the bidding tree for this bid sequence
            self.bidNode = fetchBidTreeNode(bidSeq)
        
            # Merge the bid tree node info into the team state
            self.teamState.mergeTreeNode(self, self.bidNode, self.playerRole)
            
            # Call the handler function for the current team state
            bidNotif = table.openerRebidRegistry.jump_table[self.bidNode.handler](table, self)

            # No bid node exists after a round 2 opener rebid

        elif self.playerRole == PlayerRole.RESPONDER:
            # Update the team state if a bid node exists for the current bid
            if numBids < 3:
                # Fetch the bid node from the bidding tree for this bid sequence
                self.bidNode = fetchBidTreeNode(bidSeq)
                # Merge the bid tree node info into the team state
                self.teamState.mergeTreeNode(self, self.bidNode, self.playerRole)                
                # Call the handler function for the current team state
                bidNotif = table.responderRegistry.jump_table[self.bidNode.handler](table, self)
                numBids += 1
                if numBids < 3:
                    # Update the bid notification using the bid node information
                    print("round2: cur bid seq = {}".format(self.teamState.bidSeq))
                    newBidSeq = self.teamState.bidSeq.copy()
                    newBidSeq.append(bidNotif.bid)
                    print("round2: next bid seq = {}".format(newBidSeq))
                    nextBidNode = fetchBidTreeNode(newBidSeq)
                    bidNotif.updateWithBidnode(self, nextBidNode)
            else:
                # We don't have a bid node for the third bid
                # But we still want to capture the last available bid node
                if bidSeq[0][0] == 0:
                    # First bid was a pass. Skip it.
                    twoBidSeq = bidSeq[1:]
                else:
                    twoBidSeq = bidSeq[:-1]
                self.bidNode = fetchBidTreeNode(twoBidSeq)
                bidNotif = nonNodeBidHandler(table, self)
                
        else:
            print("bridgePlayer: bidRound2: Player %s has invalid role %d" % (self.pos.name, self.playerRole.value))
        return bidNotif

    
    def bidRound3(self, table):
        if self.playerRole == PlayerRole.UNKNOWN:
            bidNotif = BidNotif(0, Suit.ALL, self.teamState)
            return bidNotif
        
        # FIX ME - debugging
        if self.pos == TablePosition.NORTH or self.pos == TablePosition.SOUTH:
            Log.write("Show team state for %s, prior to round %d bid\n" % (self.pos.name, table.roundNum))
            self.teamState.show()

        # We don't have a bid node for any round 3 bid
        # But we still want to capture the last available bid node
        bidSeq = self.teamState.bidSeq
        if bidSeq[0][0] == 0:
            # First bid was a pass. Skip it.
            twoBidSeq = bidSeq[1:3]
        else:
            twoBidSeq = bidSeq[:2]
        self.bidNode = fetchBidTreeNode(twoBidSeq)
                
        bidNotif = nonNodeBidHandler(table, self)
        return bidNotif

    
    # Bid notification handler for a player
    def bidNotification(self, table, bidder, bidNotif):
        (bidLevel, bidSuit) = (bidNotif.bid[0], bidNotif.bid[1])
        bidStr = getBidStr(bidLevel, bidSuit)
        # Log.write("bidNotif: bidder={} bid={} me={}\n".format(bidder.name, bidStr, self.pos.name))

        # Need to figure out who the bidder is?
        myPartner = whosMyPartner(self.pos)
        if bidder == myPartner:
            # Log.write("bidNotification: {} is my partner\n".format(bidder.name))
            # Partner made this bid. Update the team state bid sequence
            self.teamState.bidSeq.append(bidNotif.bid)
            bidSeq = self.teamState.bidSeq

            # Call common notification handling code
            bidNotif.notifHandler(self)

            # FIX ME - dead code
            '''
            # Can we update our team's state from a bid node?
            # We only have bid node for 2 levels of bids
            numBids = len(bidSeq)
            # check if the first bid was a pass
            if bidSeq[0][0] == 0:
                numBids -= 1
            if len(bidSeq) <= 2: 
                # Fetch the bid node from the bidding tree for this bid sequence
                self.bidNode = fetchBidTreeNode(bidSeq)
                
                # Merge the bid tree node info into the team state
                self.teamState.mergeTreeNode(self, self.bidNode, self.playerRole)
            else:
                # Log.write("bridgePlayer: bidNotif: No bid node available\n")
                # Team state is updated by the notification
                bidNotif.notifHandler(self)
            '''    
        else:
            # If opponents did not pass, then our team has competition
            if bidNotif.bid[0] > 0:
                self.teamState.competition = True
                
            # We want to update the fit state for a suit bid by opposition
            bidSuitValue = bidNotif.bid[1].value
            if bidSuitValue >= Suit.SPADE.value and bidSuitValue <= Suit.CLUB.value:
                # Log.write("bidNotification: no fit for {} bid by opposition\n".format(bidNotif.bid[1].name))
                self.teamState.suitState[bidNotif.bid[1]] = FitState.NO_SUPPORT
                
    '''
    This function is called by the card table at the end of a hand
    '''
    def processHandDone(self):
        # Clear out the team state
        self.teamState.__init__()
        
        # Turn all the cards face up
        if self.pos == TablePosition.SOUTH:
            return
        for card in self.hand.cards:
            card.faceUp = True

    '''
    This function is called by the card table to prepare for the next hand
    '''
    def nextHand(self):
        # Turn all the card face down
        for card in self.hand.cards:
            #card.faceUp = False
            card.faceUp = True
            
        # Return all the cards to the deck
        self.table.deck.cards.extend(self.hand.cards)
        del self.hand.cards[:]
