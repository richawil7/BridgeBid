'''
Bridge Player Class
A player of the game of Spades
'''

from enums import Suit, Level
from utils import *
from cardPile import CardPile
from player import Player
from bridgeHand import BridgeHand
import bid

class BridgePlayer(Player):

    def __init__(self, table, position, isHuman=False):
        super(BridgePlayer, self).__init__(table, position, isHuman)
        self.distribution = {Suit.SPADE : 0, Suit.HEART : 0, Suit.DIAMOND : 0, Suit.CLUB : 0}
        self.hand = BridgeHand(position)

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
            
        
    def computerBidRequest(self, bidsList):
        # writeLog(self.table, "bridgePlayer: computerSelectACard: position %s  lead %s\n" % (self.pos.name, self.table.leadPos.name))
            
        (nextBidLevel, nextBidSuit) = bid.calcBid(self.table, self.hand, self.table.bidsList)
        self.table.bidResponse(self.pos, nextBidLevel, nextBidSuit)
        
        
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
