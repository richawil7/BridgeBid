'''
Card Table Class

A class representing a card table on which we play some card game.
This class is dependent of the type of card game, but leaves the
display functions to the CardTableGui class.
'''
import os
from time import sleep
from constants import *
from enums import Suit, Level, TablePosition, PileOrder, DistMethod
from utils import * 
from card import Card
from cardPile import CardPile
from deck import Deck
from bridgePlayer import BridgePlayer
from bridgeHand import BridgeHand

class CardTable():

    def __init__(self, enableGui=False, humanPlaying=False):
        self.guiEnabled = enableGui
        self.humanPlayer = humanPlaying
        self.deck = Deck()
        self.players = {}
        self.suitDict = {}
        self.bidsList = []
        self.currentRound = 0
        self.currentPos = TablePosition.CONTROL
        self.leadPos = TablePosition.CONTROL
        self.outstandingBidReq = False
        self.guiTable = None
        self.newHand = False
        self.handDone = True
        self.programDone = False
        self.log_fp = None
        
        # Create 4 players
        self.players[TablePosition.NORTH] = BridgePlayer(self, TablePosition.NORTH)
        self.players[TablePosition.EAST] = BridgePlayer(self, TablePosition.EAST)
        self.players[TablePosition.SOUTH] = BridgePlayer(self, TablePosition.SOUTH, self.humanPlayer)
        self.players[TablePosition.WEST] = BridgePlayer(self, TablePosition.WEST)

        # Initialize the suit dictionary
        self.suitDict[Suit.SPADE] = {'NumCardsPlayed': 0, 'HasBeenTrumped': False}
        self.suitDict[Suit.HEART] = {'NumCardsPlayed': 0, 'HasBeenTrumped': False}
        self.suitDict[Suit.DIAMOND] = {'NumCardsPlayed': 0, 'HasBeenTrumped': False}
        self.suitDict[Suit.CLUB] = {'NumCardsPlayed': 0, 'HasBeenTrumped': False}

    def setGuiTable(self, guiTable):
        self.guiTable = guiTable

    def startHand(self):
        self.handDone = False
        self.dealCards()
        self.findNextBidder()
        if self.guiEnabled:
            self.guiTable.startHand(self.leadPos)
        self.bidRequest()
        
    def dealCards(self):
        # Open a file for information logging
        if self.guiEnabled:
            self.log_fp = open("../logs/info.log", 'w')
            writeLog(self, "Start of a new hand\n")
        
        self.deck.shuffle()
        # writeLog(self, "Deck contains {} cards\n".format(len(self.deck.cards)))
        # Create 4 empty card piles
        cardPiles = []
        for index in range(0, 4):
            cardPiles.append(BridgeHand(TablePosition.CENTER))

        # Deal cards from the deck into the 4 piles    
        for numCards in range(0, NUM_CARDS_IN_HAND):
            for index in range(0, 4):
                # Get the next card from the deck
                card = self.deck.selectCard()
                cardPiles[index].addCard(card)

        # Calculate points for each pile
        # Find the 2 piles with the highest points
        maxPoints = 0
        indexOfBestPile = 9
        for index in range(0, 4):
            numPoints = cardPiles[index].evalHand(DistMethod.LONG)
            if numPoints > maxPoints:
                maxPoints = numPoints
                indexOfBestPile = index
                
        maxPoints = 0
        indexOfSecondBestPile = 9
        for index in range(0, 4):
            if index == indexOfBestPile:
                continue
            numPoints = cardPiles[index].evalHand(DistMethod.LONG)
            if numPoints > maxPoints:
                maxPoints = numPoints
                indexOfSecondBestPile = index

        # Give the 2 best hands to North and South
        if indexOfBestPile > indexOfSecondBestPile:
            self.players[TablePosition.NORTH].hand = cardPiles[indexOfBestPile]
            self.players[TablePosition.SOUTH].hand = cardPiles[indexOfSecondBestPile]
        else:
            self.players[TablePosition.NORTH].hand = cardPiles[indexOfSecondBestPile]
            self.players[TablePosition.SOUTH].hand = cardPiles[indexOfBestPile]

        # Give the other 2 hands to East and West
        eastHasHand = False
        for index in range(0, 4):
            if index == indexOfBestPile or index == indexOfSecondBestPile:
                continue
            if eastHasHand:
                self.players[TablePosition.WEST].hand = cardPiles[index]
            else:
                self.players[TablePosition.EAST].hand = cardPiles[index]
                eastHasHand = True
            
        # Sort the cards in each hand
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
                    
            player = self.players[pos]
            hand = player.hand
            hand.sort()
            if pos == TablePosition.SOUTH:
                # Turn cards face up
                for card in hand.cards:
                    card.faceUp = True
            if self.guiEnabled:
                self.guiTable.cardDealt(pos, hand)

            # Calculate the bid for each hand
            writeLog(self, "PLAYER: {} ****************\n".format(player.pos.name))

    def findNextBidder(self):
        if self.leadPos == TablePosition.CONTROL:
            # Start of the program. Computer bids first.
            self.leadPos = TablePosition.NORTH
        elif self.leadPos == TablePosition.NORTH:
            self.leadPos = TablePosition.EAST
        elif self.leadPos == TablePosition.EAST:
            self.leadPos = TablePosition.SOUTH
        elif self.leadPos == TablePosition.SOUTH:
            self.leadPos = TablePosition.WEST
        elif self.leadPos == TablePosition.WEST:
            self.leadPos = TablePosition.NORTH
            
        self.currentPos = self.leadPos

    def bidRequest(self):
        player = self.players[self.currentPos]
        print("cardTable: bidReq: position %s" % player.pos.name)
        self.outstandingBidReq = True
        player.bidRequest(self.bidsList)

    def bidResponse(self, pos, bidLevel, bidSuit):
        print("cardTable: bidResponse from %s: %d%s" % (pos.name, bidLevel, bidSuit.name))
        self.outstandingBidReq = False
        self.bidsList.append((bidLevel, bidSuit))
        
        # Update the GUI bid board with this player's bid
        if self.guiEnabled:
            self.guiTable.updateBids(self.currentPos, bidLevel, bidSuit)

        if bidLevel > 7:
            self.processHandDone()
            return
        
        (nextPos, newRound) = getNextPosition(self.currentPos, self.leadPos)
        self.currentPos = nextPos
        if newRound:
            self.currentRound += 1
            
        self.bidRequest()

            
    def processHandDone(self):
        self.handDone = True
        
        # Notify each player that the hand has completed
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
            player = self.players[pos]
            player.processHandDone()
            
        if self.guiEnabled:
            self.guiTable.processHandDone()

        # Close the logging file
        self.log_fp.close()
        # Delete the previously saved log file
        os.remove("../logs/save.log")
        # Rename the logging file
        os.rename("../logs/info.log", "../logs/save.log")


    '''
    This function is called when the user asks to play another hand
    '''       
    def nextHand(self):
        print("cardTable: nextHand entry")
        # Prepare for next hand
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
            player = self.players[pos]
            player.nextHand()
            
        self.guiTable.nextHand()
        del self.bidsList[:]
        self.newHand = True
        self.startHand()

    def flushLog(self):
        self.log_fp.flush()