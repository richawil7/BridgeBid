'''
Bridge Player Class
A player of the game of Spades
'''

from enums import Suit, Level, TeamRole, PlayerRole
from utils import *
from bidNode import *
from cardPile import CardPile
from teamState import TeamState
from player import Player
from bridgeHand import BridgeHand
from bidUtils import *
from openBid import *
from responderBid import *

class BridgePlayer(Player):

    def __init__(self, table, position, isHuman=False):
        super(BridgePlayer, self).__init__(table, position, isHuman)
        self.distribution = {Suit.SPADE : 0, Suit.HEART : 0, Suit.DIAMOND : 0, Suit.CLUB : 0}
        self.seat = 0
        self.playerRole = PlayerRole.UNKNOWN
        self.hand = BridgeHand(position)
        self.teamState = TeamState()
        self.lastBid = (Level.LOW, Suit.ALL)
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
        self.teamState.minTeamPts = hcPoints
        self.teamState.maxTeamPts = hcPoints + distPoints
        self.teamState.candidateSuit = self.hand.findLongestSuit()
        
    def bidRequest(self, table, listOfBids):
        if self.isHuman:
            curPos = table.currentPos
            player = table.players[curPos]
            # Ask the computer to calculate the bid for the human
            # But later it will be ignored
            player.computerBidRequest(table, table.hasOpener, table.competition, table.roundNum, table.bidsList, self.isHuman, player.hand)
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
        writeLog(table, "BidReq: pos={} hasOpener={} compet={} roundNum={}\n".format(self.pos.name, hasOpener, competition, roundNum))

        if roundNum == 1:
            (bidLevel, bidSuit) = self.bidRound1(table)

        elif roundNum == 2:
            (bidLevel, bidSuit) = self.bidRound2(table)

        elif roundNum == 3:
            (bidLevel, bidSuit) = self.bidRound3(table)

        else:
            bidLevel = 0
            bidSuit = Suit.ALL
        
        bidStr = getBidStr(bidLevel, bidSuit)
        writeLog(self.table, "BidRsp: %s as %s bids %s\n" % (self.pos.name, self.playerRole.name, bidStr))
        
        # Only submit the bid if the computer is this player
        if not isHuman:
            self.table.bidResponse(self.pos, bidLevel, bidSuit)

    def bidRound1(self, table):
        # Figure out this player's bidding role
        self.playerRole = getMyPlayerRole(table, self)
        
        # Get the sequence of bids made by this partnership
        bidSeq = getTeamBidSequence(table, self.pos)

        # Fetch the bid node from the bidding tree for this bid sequence
        self.bidNode = fetchBidTreeNode(bidSeq)

        # Merge the bid tree node info into the team state
        self.teamState.mergeTreeNode(self, self.bidNode, self.playerRole)
        
        if self.playerRole == PlayerRole.RESPONDER:
            # Call the handler function for the current team state
            (bidLevel, bidSuit) = table.responderRegistry.jump_table[self.bidNode.handler](table, self)
        else:
            # Call the handler function for the current team state
            (bidLevel, bidSuit) = table.openerRegistry.jump_table[self.bidNode.handler](table, self)

        # Save the most recent bid
        self.lastBid = (bidLevel, bidSuit)

        return (bidLevel, bidSuit)


    def bidRound2(self, table):
        # Get the sequence of bids made by this partnership
        bidSeq = getTeamBidSequence(table, self.pos)
        numBids = len(bidSeq)
        # Check if the first bid was a pass
        if bidSeq[0][0] == 0:
            # print("First bid was a pass")
            numBids -= 1
            
        # Figure out this player's bidding role
        if self.playerRole == PlayerRole.UNKNOWN:
            self.playerRole = getMyPlayerRole(table, self)

        if self.playerRole == PlayerRole.UNKNOWN:
            # print("bridgePlayer: bidRound2: Player %s STILL has unknown role %s" % (self.pos.name, self.playerRole.name))
            return (0, Suit.ALL)
            
        elif self.playerRole == PlayerRole.OPENER:
            # Fetch the bid node from the bidding tree for this bid sequence
            self.bidNode = fetchBidTreeNode(bidSeq)
        
            # Merge the bid tree node info into the team state
            self.teamState.mergeTreeNode(self, self.bidNode, self.playerRole)
            
            # Call the handler function for the current team state
            (bidLevel, bidSuit) = table.openerRebidRegistry.jump_table[self.bidNode.handler](table, self)

        elif self.playerRole == PlayerRole.RESPONDER:
            if numBids >= 3:
                # Can't use bidding trees for responder rebid
                (bidLevel, bidSuit) = stubBid(table, table.bidsList)
            else:
                # Call the handler function for the current team state
                (bidLevel, bidSuit) = table.responderRegistry.jump_table[self.bidNode.handler](table, self)

        else:
            print("bridgePlayer: bidRound2: Player %s has invalid role %d" % (self.pos.name, self.playerRole.value))

        bidStr = getBidStr(bidLevel, bidSuit)
        self.lastBid = (bidLevel, bidSuit)
        return (bidLevel, bidSuit)

    
    def bidRound3(self, table):
        if self.playerRole == PlayerRole.UNKNOWN:
            return (0, Suit.ALL)
        
        (bidLevel, bidSuit) = stubBid(table, table.bidsList)
        bidStr = getBidStr(bidLevel, bidSuit)
        return (bidLevel, bidSuit)

    
    def bidNotification(self, table, bidder, bidLevel, bidSuit):
        bidStr = getBidStr(bidLevel, bidSuit)
        # writeLog(table, "bidNotif: bidder={} bid={} me={}\n".format(bidder.name, bidStr, self.pos.name))
        # Need to figure out who the bidder is?
        myPartner = whosMyPartner(self.pos)

        if bidder == self.pos:
            # I made this bid. Just need to add bid to the team state
            self.teamState.addTeamBid(bidLevel, bidSuit)
        elif bidder == myPartner:
            # Partner this bid
            self.teamState.addTeamBid(bidLevel, bidSuit)
            # Get the sequence of bids made by this partnership
            bidSeq = getTeamBidSequence(table, self.pos)

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
                writeLog(table, "bridgePlayer: bidNotif: Skipping bid node\n")
                
        # FIX ME. Debug that can be removed
        #if self.pos == TablePosition.NORTH and bidder == TablePosition.SOUTH:
        #    bidStr = getBidStr(bidLevel, bidSuit)
        #    print("bidNotif: show NORTH state after SOUTH bid of %s" % bidStr)
        #    self.teamState.show()

            
    def bidRound1Old(self, table, hasOpener, competition, roundNum, bidsList, hand):
        # FIX ME: dead code
        bidLevel = 0
        bidSuit = Suit.ALL
        # Determine this player's bidding state
        if not hasOpener and not competition:
            # No one has opened yet
            iCanOpen = canIOpen(self.hand, competition, self.seat) 
            if iCanOpen:
                self.playerRole = PlayerRole.OPENER
                (bidLevel, bidSuit) = calcOpenBid(self.hand)

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
                        writeLog(self.table, "bridgePlayer: compBidReq: partner opened\n")
                    self.playerRole = PlayerRole.RESPONDER
                    (bidLevel, bidSuit) = responderBid(self.table, self.hand, bidsList)
                else:
                    # My partner passed
                    writeLog(self.table, "bridgePlayer: compBidReq: partner passed\n")
            else:
                iCanOpen = canIOpen(self.hand, competition, self.seat) 
                if iCanOpen:
                    self.playerRole = PlayerRole.OPENER
                    (bidLevel, bidSuit) = calcOpenBid(self.hand)
                else:
                    bidLevel = 0
        return (bidLevel, bidSuit)

    def bidRound2Old(self, table, hasOpener, competition, roundNum, bidsList, hand):
        bidLevel = 0
        bidSuit = Suit.ALL
        if self.playerRole == PlayerRole.UNKNOWN:
            if self.seat <= 2:
                # Need to check if my partner bid in round 1
                partnerBidIdx = self.seat + 2 - 1
                partnerBid = bidsList[partnerBidIdx][0]
                if partnerBid > 0:
                    # My partner opened
                    self.playerRole == PlayerRole.RESPONDER
                    (bidLevel, bidSuit) = responderBid(self.table, self.hand, bidsList)
        elif self.playerRole == PlayerRole.OPENER:
            #(bidLevel, bidSuit) = openerRebid(self.table, self.hand, bidsList)
            (bidLevel, bidSuit) = stubBid(table, bidsList)
        elif self.playerRole == PlayerRole.RESPONDER:
            #(bidLevel, bidSuit) = responderRebid(self.table, self.hand, bidsList)
            (bidLevel, bidSuit) = stubBid(table, bidsList)
        return (bidLevel, bidSuit)

    
    '''
    This function is called by the card table at the end of a hand
    '''
    def processHandDone(self):
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
