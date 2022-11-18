'''
Card Table GUI Class

A class representing a card table on which we play some card game.
This class is independent of the type of card game.
It is mostly a GUI helper, setting up frames for each player and a 
center frame for showing played cards.
'''

import tkinter as tk
from time import sleep
from enums import TablePosition
from cardPile import CardPile
from card import Card

class CardTableGui():

    def __init__(self, app, tableWidth, tableHeight):
        self.app = app
        self.width = tableWidth
        self.height = tableHeight
        self.tableFrames = {}
        self.centerCardDict = {}

    def setFrameByPosition(self, tablePosition, tableFrame):
        self.tableFrames[tablePosition] = tableFrame

    def getFrameByPosition(self, tablePosition):
        return self.tableFrames[tablePosition]

    def startHand(self, leadPos):
        frame = self.getFrameByPosition(TablePosition.CONTROL)
        frame.createBidBoard(leadPos)
        
    def cardDealt(self, tablePosition, hand):
        hand.setGuiParams(self, tablePosition)
        frame = self.getFrameByPosition(tablePosition)
        frame.draw_frame()
        #sleep(1)
        
    def cardPlayed(self, tablePosition, hand, card):
        hand.setGuiParams(self, tablePosition)
        frame = self.getFrameByPosition(tablePosition)
        #frame.setCardPile(hand)
        # Accept the card in the center
        centerFrame = self.getFrameByPosition(TablePosition.CENTER)
        self.centerCardDict[tablePosition] = card
        centerDesc = CardPile.setCenterGuiParams(self, self.centerCardDict)
        frame.draw_frame()        
        centerFrame.draw_frame()

    def roundDone(self):
        sleep(2)
        self.centerCardDict.clear()
        centerFrame = self.getFrameByPosition(TablePosition.CENTER)
        centerFrame.clear()
        
    def updateBids(self, pos, level, suit):
        controlFrame = self.getFrameByPosition(TablePosition.CONTROL)
        controlFrame.updateBids(self.app.table, pos, level, suit)

    def processHandDone(self):
        for pos in TablePosition:
            if pos == TablePosition.CONTROL or pos == TablePosition.CENTER:
                continue
            frame = self.getFrameByPosition(pos)
            frame.draw_frame()        
        return

    def nextHand(self):
        print("cardTableGui: nextHand")
        # Clear all the frames
        for pos in TablePosition:
            frame = self.tableFrames[pos]
            if pos == TablePosition.CENTER:
                continue
            elif pos == TablePosition.CONTROL:
                frame.nextHand()
            else:
                frame.clear()


    def cardSelectHandler(self, event):
        # Determine from which canvas came the event
        for pos, frame in self.tableFrames.items():
            if frame.canvas == event.widget:
                #print("Position={} x={} y={}".format(frame.pos.name, event.x, event.y))
                break
        player = self.app.table.players[pos]
        # Only process a card if player is human
        if player.isHuman:
            # Only process a card if player is the current player
            if pos == self.app.table.currentPos:
                cardSelected = player.hand.findCardByPoint(event.x, event.y)
                if cardSelected != None:
                    player.hand.removeCard(cardSelected)
                    player.biddingHand.deleteCard(cardSelected.suit, cardSelected.level)
                    # Once a card is selected, no longer a new hand
                    self.app.table.newHand = False
                    # Tell the card table the card which was selected
                    self.app.table.cardPlayed(cardSelected)

