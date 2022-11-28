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
        self.bidsList = []
        self.roundNum = 0
        self.hasOpener = False
        self.competition = False
        self.currentPos = TablePosition.CONTROL
        self.leadPos = TablePosition.CONTROL
        self.outstandingBidReq = False
        self.guiTable = None
        self.handDone = True
        self.programDone = False
        self.log_fp = None
        
        # Create 4 players
        self.players[TablePosition.NORTH] = BridgePlayer(self, TablePosition.NORTH)
        self.players[TablePosition.EAST] = BridgePlayer(self, TablePosition.EAST)
        self.players[TablePosition.SOUTH] = BridgePlayer(self, TablePosition.SOUTH, self.humanPlayer)
        self.players[TablePosition.WEST] = BridgePlayer(self, TablePosition.WEST)

    def setGuiTable(self, guiTable):
        self.guiTable = guiTable

    def startHand(self):
        self.handDone = False
        self.dealCards()
        self.hasOpener = False
        self.competition = False
        self.findNextBidder()
        self.roundNum = 1
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
            player = self.players[pos]
            player.startHand(self.leadPos)
            
        if self.guiEnabled:
            self.guiTable.startHand(self.leadPos)
        self.bidRequest()
        
    def dealCards(self):
        # Open a file for information logging
        if self.guiEnabled:
            self.log_fp = open("../logs/info.log", 'w')
            writeLog(self, "Start of a new hand\n")
        
        self.deck.shuffle()
        
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
            (numPoints, distPoints) = cardPiles[index].evalHand(DistMethod.LONG)
            if numPoints > maxPoints:
                maxPoints = numPoints
                indexOfBestPile = index
                
        maxPoints = 0
        indexOfSecondBestPile = 9
        for index in range(0, 4):
            if index == indexOfBestPile:
                continue
            (numPoints, distPoints) = cardPiles[index].evalHand(DistMethod.LONG)
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


    def findNextBidder(self):
        if self.leadPos == TablePosition.CONTROL:
            # Start of the program. Computer bids first.
            self.leadPos = TablePosition.NORTH
        else:
            (nextBidder, isLeader) = getNextPosition(self.leadPos, self.leadPos)
            self.leadPos = nextBidder;
        self.currentPos = self.leadPos
        writeLog(self, "cardTable: findNextBidder: position %s\n" % self.leadPos.name)

    def bidRequest(self):
        player = self.players[self.currentPos]
        writeLog(self, "cardTable: bidRequest for %s in round %d\n" % (player.pos.name, self.roundNum))
        self.outstandingBidReq = True
        player.bidRequest(self.bidsList)

    def bidResponse(self, pos, bidLevel, bidSuit):
        bidStr = getBidStr(bidLevel, bidSuit)
        writeLog(self, "cardTable: bidResponse from %s: %s\n" % (pos.name, bidStr))
        self.outstandingBidReq = False
        if self.hasOpener:
            if bidLevel > 0:
                # Was this bid received from the opener's competitor?
                if self.competition == False:
                    # Check the last bid on the bid list
                    if self.bidsList[-1][0] > 0:
                        self.competition = True
                        writeLog(self, "cardTable: bidResponse: table in competition\n")
                    else:
                        if len(self.bidsList) >= 3 and self.bidsList[-3][0] > 0:
                            self.competition = True
                            writeLog(self, "cardTable: bidResponse: table in competition\n")
        elif bidLevel > 0:
            self.hasOpener = True
            writeLog(self, "cardTable: bidResponse: table has opener\n")
        self.bidsList.append((bidLevel, bidSuit))
        
        # Update the GUI bid board with this player's bid
        if self.guiEnabled:
            self.guiTable.updateBids(self.currentPos, bidLevel, bidSuit)

        # Provide a development hook to bail out of bidding loop
        if bidLevel > 7:
            self.processHandDone()
            return
        
        # Check if bidding is complete
        if len(self.bidsList) >= 4:
            if self.bidsList[-1][0] == 0 and \
               self.bidsList[-2][0] == 0 and \
               self.bidsList[-3][0] == 0:
                self.processHandDone()
                return
            
        (nextPos, newRound) = getNextPosition(self.currentPos, self.leadPos)
        self.currentPos = nextPos
        if newRound:
            self.roundNum += 1
            
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
        # Prepare for next hand
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
            player = self.players[pos]
            player.nextHand()
            
        self.guiTable.nextHand()
        del self.bidsList[:]
        self.startHand()

    def flushLog(self):
        self.log_fp.flush()
