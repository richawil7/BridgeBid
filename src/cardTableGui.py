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
        # Clear all the frames
        for pos in TablePosition:
            frame = self.tableFrames[pos]
            if pos == TablePosition.CENTER:
                continue
            elif pos == TablePosition.CONTROL:
                frame.nextHand()
            else:
                frame.clear()

