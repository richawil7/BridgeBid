'''
Control Frame Class

A class representing the control frame within a card table.
This class is somewhat dependent of the type of card game, as it will
show game control widgets and game status (e.g. player's scores).
'''

import tkinter as tk
from enums import TablePosition, Suit
from frame import TableFrame
from utils import *

class ControlFrame(TableFrame):

    def __init__(self, app, rootFrame, frameSide):
        super(ControlFrame, self).__init__(app, rootFrame, TablePosition.CONTROL, frameSide)

        # Create a table control frame in the parent control frame
        self.tableCtlFrame = tk.Frame(self.tkFrame)
        self.tableCtlFrame.pack(padx=0, pady=20, side=tk.BOTTOM)
        
        # Create a bid frame in the parent control frame
        self.bidRowIdx = 0
        self.bidColIdx = 0
        self.bidFrame = tk.Frame(self.tkFrame)
        self.bidFrame.pack(padx=0, pady=50, side=tk.TOP)

        # Create labels for the bids table
        self.bidLabel = []
        
        # Create a button to request another hand
        tk.Button(self.tableCtlFrame, text='Next Hand', command=self.app.table.nextHand).pack(side="left", padx=5)
        
        # Create a button to flush the log file
        tk.Button(self.tableCtlFrame, text='Flush Log', command=self.app.table.flushLog).pack(side="left", padx=5)


    def createBidBoard(self, leadPos):
        pos = leadPos
        
        # Labels for header row
        label = tk.Label(self.bidFrame, text=pos.name, bg="green", fg="white")
        self.bidLabel.append(label)
        label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        (pos, dummy) = getNextPosition(pos, leadPos)
        label = tk.Label(self.bidFrame, text=pos.name, bg="green", fg="white")
        self.bidLabel.append(label)
        label.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        (pos, dummy) = getNextPosition(pos, leadPos)
        label = tk.Label(self.bidFrame, text=pos.name, bg="green", fg="white")
        self.bidLabel.append(label)
        label.grid(row=0, column=2, sticky='w', padx=5, pady=5)

        (pos, dummy) = getNextPosition(pos, leadPos)
        label = tk.Label(self.bidFrame, text=pos.name, bg="green", fg="white")
        self.bidLabel.append(label)
        label.grid(row=0, column=3, sticky='w', padx=5, pady=5)


    def updateBids(self, table, position, bidLevel, bidSuit):
        print("updateBids: lead=%s pos=%s lvl=%d suit=%s" % (table.leadPos, position, bidLevel, bidSuit))
        if position == table.leadPos:
            self.bidRowIdx += 1
            self.bidColIdx = 0
        elif position.value > table.leadPos.value:
            self.bidColIdx = position.value - table.leadPos.value
        else:
            self.bidColIdx = (4 - table.leadPos.value + position.value) % 4

        if bidLevel == 0:
            bidStr = "Pass"
        elif bidLevel > 7:
            bidStr = "Done"
        else:
            bidStr = "%s" % bidLevel
            if bidSuit == Suit.SPADE:
                bidStr += "S"
            elif bidSuit == Suit.HEART:
                bidStr += "H"
            elif bidSuit == Suit.DIAMOND:
                bidStr += "D"
            elif bidSuit == Suit.CLUB:
                bidStr += "C"
            elif bidSuit == Suit.NOTRUMP:
                bidStr += "NT"

        bidLabel = tk.Label(self.bidFrame, text=bidStr, bg="yellow", fg="black")
        bidLabel.grid(row=self.bidRowIdx, column=self.bidColIdx, sticky='w', padx=5, pady=5)
        
    def processHandDone(self):
        # Show the bid that should have been reached
        # TDB
        pass

    def nextHand(self):
        print("controlFrame: nextHand entry")
        self.bidRowIdx = 0
        self.bidColIdx = 0
        # remove bid labels from the frame
        for label in self.bidFrame.grid_slaves():
            label.grid_forget()
            
        
