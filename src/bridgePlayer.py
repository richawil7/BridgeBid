'''
Bridge Player Class
A player of the game of Spades
'''

from enums import Suit, Level, TeamRole, PlayerRole
from utils import *
from cardPile import CardPile
from player import Player
from bridgeHand import BridgeHand
from bid import *

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
            # if self.table.guiEnabled:
            # RW HACK - only support bids via stdin for now
            if True:
                #print("Pick a card to play by clicking on it")
                bidLevel = int(input("Enter the bid level"))
                suitStr = input("Enter the suit")
                if suitStr == "C":
                    bidSuit = Suit.CLUB
                elif suitStr == "D":
                    bidSuit = Suit.DIAMOND
                elif suitStr == "H":
                    bidSuit = Suit.HEART
                elif suitStr == "S":
                    bidSuit = Suit.SPADE
                elif suitStr == "N":
                    bidSuit = Suit.NOTRUMP
                else:
                    bidSuit = Suit.NOTRUMP
                self.table.bidResponse(self.pos, bidLevel, bidSuit)

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
        writeLog(table, "bridgePlayer:compBidReq: pos={} hasOpener={} compet={} roundNum={}\n".format(self.pos, hasOpener, competition, roundNum))

        bidLevel = 0
        bidSuit = Suit.ALL
        # Determine this player's bidding state
        if not hasOpener and not competition:
            writeLog(self.table, "bridgePlayer: compBidReq: no opener yet\n")
            # No one has opened yet
            iCanOpen = canIOpen(self.hand, competition, self.seat) 
            if iCanOpen:
                self.teamRole = TeamRole.OFFENSE
                self.playerRole = PlayerRole.OPENER
                (bidLevel, bidSuit) = calcOpenBid(self.hand)
            else:
                bidLevel = 0

        elif not hasOpener and competition:
            print("bridgePlayer: computerBidReq: Error-invalid state ")

        elif hasOpener:
            writeLog(self.table, "bridgePlayer: compBidReq: table has opener\n")
            # Check if my partner was the opener
            partnerBidIdx = self.seat - 2 - 1
            partnerBid = bidsList[partnerBidIdx][0]
            if partnerBid > 0:
                # My partner opened
                writeLog(self.table, "bridgePlayer: compBidReq: partner opened\n")
                self.teamRole = TeamRole.OFFENSE
                self.playerRole = PlayerRole.RESPONDER
                # RW: temporary hack
                bidLevel = 0
            else:
                # My partner passed
                writeLog(self.table, "bridgePlayer: compBidReq: partner passed\n")
                iCanOpen = canIOpen(self.hand, competition, self.seat) 
                if iCanOpen:
                    self.teamRole = TeamRole.OFFENSE
                    self.playerRole = PlayerRole.OPENER
                    (bidLevel, bidSuit) = calcOpenBid(self.hand)
                else:
                    bidLevel = 0

        bidStr = getBidStr(bidLevel, bidSuit)
        writeLog(self.table, "bridgePlayer: compBidReq: bid %s\n" % bidStr)
        self.table.bidResponse(self.pos, bidLevel, bidSuit)

        
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
