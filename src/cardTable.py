'''
Card Table Class

A class representing a card table on which we play some card game.
This class is dependent of the type of card game, but leaves the
display functions to the CardTableGui class.
'''
import os
import json
from time import sleep
from constants import *
from infoLog import Log
from enums import Suit, Level, TablePosition, PileOrder, DistMethod
from utils import * 
from card import Card
from cardPile import CardPile
from deck import Deck
from bridgePlayer import BridgePlayer
from bridgeHand import BridgeHand
from openBid import OpenerRegistry
from responderBid import ResponderRegistry
from openerRebid import OpenerRebidRegistry

class CardTable():

    def __init__(self, enableGui=False, humanPlaying=False, replayHand=False):
        self.guiEnabled = enableGui
        self.humanPlayer = humanPlaying
        self.replayHand = replayHand
        self.deck = Deck()
        self.players = {}
        self.openerRegistry = OpenerRegistry()
        self.responderRegistry = ResponderRegistry()
        self.openerRebidRegistry = OpenerRebidRegistry()
        self.bidsList = []
        self.highestBid = (0, Suit.ALL)
        self.roundNum = 0
        self.hasOpener = False
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
        # Open a file for information logging
        Log.open()
        if self.guiEnabled:
            Log.write("Start of a new hand\n")
        self.handDone = False
        self.dealCards()
        self.hasOpener = False
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
        

    def dealLastHands(self):
        # Open the file containing the previous hands
        hand_fp = open("../logs/lastHands.json", 'r')
        Log.write("Loading the previous hand\n")
        handsJson = hand_fp.read()
        handsDict = json.loads(handsJson)
        
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
                    
            player = self.players[pos]
            cardTupleList = handsDict[pos.name]
            for cardTuple in cardTupleList:
                # Find the card in the deck
                card = self.deck.deleteCard(Suit(cardTuple[1]), Level(cardTuple[0]))
                card.position = pos
                # FIX ME: for debugging, turn all cards up
                #if pos == TablePosition.SOUTH:
                if True:
                    card.faceUp = True
                player.hand.cards.append(card)
                
            if self.guiEnabled:
                self.guiTable.cardDealt(pos, player.hand)

                
    def dealNewHands(self):
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
            (numPoints, distPoints) = cardPiles[index].evalHand(DistMethod.HCP_LONG)
            if numPoints > maxPoints:
                maxPoints = numPoints
                indexOfBestPile = index
                
        maxPoints = 0
        indexOfSecondBestPile = 9
        for index in range(0, 4):
            if index == indexOfBestPile:
                continue
            (numPoints, distPoints) = cardPiles[index].evalHand(DistMethod.HCP_LONG)
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
        handsDict = {}
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
                    
            player = self.players[pos]
            hand = player.hand
            hand.sort()

            # Store this hand in a dictionary
            cardList = []
            for card in hand.cards:
                cardTuple = (card.level.value, card.suit.value)                
                cardList.append(cardTuple)
            handsDict[pos.name] = cardList
            
            # FIX ME: for debugging, turn all cards up
            #if pos == TablePosition.SOUTH:
            if True:
                # Turn cards face up
                for card in hand.cards:
                    card.faceUp = True
            if self.guiEnabled:
                self.guiTable.cardDealt(pos, hand)
                
        # Write the hand dictionary out to a file
        hand_fp = open("../logs/lastHands.json", 'w')
        hand_fp.write(json.dumps(handsDict))

        
    def dealCards(self):
        # Do we want a new hand or to replay the previous hand?
        if self.replayHand:
            self.dealLastHands()
        else:
            self.dealNewHands()

    def findNextBidder(self):
        if self.leadPos == TablePosition.CONTROL:
            # Start of the program. Computer bids first.
            self.leadPos = TablePosition.NORTH
        else:
            (nextBidder, isLeader) = getNextPosition(self.leadPos, self.leadPos)
            self.leadPos = nextBidder;
        self.currentPos = self.leadPos
        

    def bidRequest(self):
        player = self.players[self.currentPos]
        self.outstandingBidReq = True
        player.bidRequest(self, self.bidsList)

        
    def bidResponse(self, bidder, bidNotif):
        (bidLevel, bidSuit) = (bidNotif.bid[0], bidNotif.bid[1])        
        bidStr = getBidStr(bidLevel, bidSuit)

        player = self.players[bidder]
        if bidder == TablePosition.NORTH or bidder == TablePosition.SOUTH:
            Log.write("BidRsp: %s as %s bids %s\n" % (bidder.name, player.playerRole.name, bidStr))
        
        # Check if the computer and human agreed on this bid
        if player.isHuman:
            if bidLevel != player.lastBid[0] or bidSuit != player.lastBid[1]:
                computerBidStr = getBidStr(player.lastBid[0], player.lastBid[1])
                print("Computer bid %s != Human bid %s" % (computerBidStr, bidStr))
            # Overwrite the last bid with what the human bid
            player.lastBid = (bidLevel, bidSuit)

        self.outstandingBidReq = False
        if bidLevel > 0 and self.hasOpener == False:
            self.hasOpener = True

        # Verify this bid is higher than the previous highest bid
        if bidLevel > 0:
            if bidLevel < self.highestBid[0]:
                print("bidResponse: invalid bid of %s" % bidStr)
            elif bidLevel == self.highestBid[0] and bidSuit.value >= self.highestBid[1].value:
                print("bidResponse: invalid bid of %s" % bidStr)
            self.highestBid = bidNotif.bid
            
        # Record the bid on both the table and bidder's bid list
        self.bidsList.append((bidLevel, bidSuit))
        
        player.teamState.bidSeq.append((bidLevel, bidSuit))
        # The bidder's partner will be updated via a bid notification
                
        # Update the GUI bid board with this player's bid
        if self.guiEnabled:
            self.guiTable.updateBids(self.currentPos, bidLevel, bidSuit)

        # Notify each player that a bid has been received
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
            if pos == bidder:
                # No need to notify the bidder
                continue
            player = self.players[pos]
            player.bidNotification(self, bidder, bidNotif)
            
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
        print("Hand completed")
        Log.write("Hand completed\n")
        Log.close()

        # Rotate the info log to the save log
        Log.rotate()


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

