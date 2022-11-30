'''
Bridge Player Class
A player of the game of Spades
'''

from enums import Suit, Level, TeamRole, PlayerRole
from utils import *
from cardPile import CardPile
from player import Player
from bridgeHand import BridgeHand
from bidUtils import *
from openBid import *
from openRsp import *

class BridgePlayer(Player):

    def __init__(self, table, position, isHuman=False):
        super(BridgePlayer, self).__init__(table, position, isHuman)
        self.distribution = {Suit.SPADE : 0, Suit.HEART : 0, Suit.DIAMOND : 0, Suit.CLUB : 0}
        self.seat = 0
        self.teamRole = TeamRole.UNKNOWN
        self.playerRole = PlayerRole.UNKNOWN
        self.hand = BridgeHand(position)

    def startHand(self, leadPos):
        self.teamRole = TeamRole.UNKNOWN
        self.playerRole = PlayerRole.UNKNOWN
        # Calculate which seat I'm sitting in
        if self.pos.value >= leadPos.value:
            self.seat = self.pos.value - leadPos.value + 1
        else:
            self.seat = 4 + self.pos.value - leadPos.value + 1
        
    def bidRequest(self, listOfBids):
        if self.isHuman:
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
    def computerBidRequest(self, table, hasOpener, competition, roundNum, bidsList, hand):
        # writeLog(table, "bridgePlayer:compBidReq: pos={} hasOpener={} compet={} roundNum={}\n".format(self.pos, hasOpener, competition, roundNum))

        if roundNum == 1:
            (bidLevel, bidSuit) = self.bidRound1(table, hasOpener, competition, roundNum, bidsList, hand)

        elif roundNum == 2:
            (bidLevel, bidSuit) = self.bidRound2(table, hasOpener, competition, roundNum, bidsList, hand)

        elif roundNum == 3:
            (bidLevel, bidSuit) = self.bidRound3(table, hasOpener, competition, roundNum, bidsList, hand)

        else:
            bidLevel = 0
            bidSuit = Suit.ALL
        
        # bidStr = getBidStr(bidLevel, bidSuit)
        # writeLog(self.table, "bridgePlayer: compBidReq: bid %s\n" % bidStr)
        self.table.bidResponse(self.pos, bidLevel, bidSuit)
        
    def bidRound1(self, table, hasOpener, competition, roundNum, bidsList, hand):
        bidLevel = 0
        bidSuit = Suit.ALL
        # Determine this player's bidding state
        if not hasOpener and not competition:
            # No one has opened yet
            iCanOpen = canIOpen(self.hand, competition, self.seat) 
            if iCanOpen:
                self.teamRole = TeamRole.OFFENSE
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
                    self.teamRole = TeamRole.OFFENSE
                    self.playerRole = PlayerRole.RESPONDER
                    (bidLevel, bidSuit) = openResponse(self.table, self.hand, bidsList)
                else:
                    # My partner passed
                    writeLog(self.table, "bridgePlayer: compBidReq: partner passed\n")
            else:
                iCanOpen = canIOpen(self.hand, competition, self.seat) 
                if iCanOpen:
                    self.teamRole = TeamRole.OFFENSE
                    self.playerRole = PlayerRole.OPENER
                    (bidLevel, bidSuit) = calcOpenBid(self.hand)
                else:
                    bidLevel = 0
        return (bidLevel, bidSuit)

    def bidRound2(self, table, hasOpener, competition, roundNum, bidsList, hand):
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
                    (bidLevel, bidSuit) = openResponse(self.table, self.hand, bidsList)
                    self.teamRole == TeamRole.OFFENSE
                else:
                    self.teamRole == TeamRole.DEFENSE
        elif self.playerRole == PlayerRole.OPENER:
            #(bidLevel, bidSuit) = openerRebid(self.table, self.hand, bidsList)
            (bidLevel, bidSuit) = stubBid(table, bidsList)
        elif self.playerRole == PlayerRole.RESPONDER:
            #(bidLevel, bidSuit) = responderRebid(self.table, self.hand, bidsList)
            (bidLevel, bidSuit) = stubBid(table, bidsList)
        return (bidLevel, bidSuit)

    def bidRound3(self, table, hasOpener, competition, roundNum, bidsList, hand):
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
            card.faceUp = False
            
        # Return all the cards to the deck
        self.table.deck.cards.extend(self.hand.cards)
        del self.hand.cards[:]
