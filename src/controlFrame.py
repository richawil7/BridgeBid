'''
Control Frame Class

A class representing the control frame within a card table.
This class is somewhat dependent of the type of card game, as it will
show game control widgets and game status (e.g. player's scores).
'''

import tkinter as tk
from enums import TablePosition, Suit, PlayerRole
from frame import TableFrame
from bidUtils import *
from utils import *


BidLevels = [0, 1, 2, 3, 4, 5, 6, 7]
BidSuits = ['Club', 'Diamond', 'Heart', 'Spade', 'NoTrump']

class ControlFrame(TableFrame):

    def __init__(self, app, rootFrame, frameSide):
        super(ControlFrame, self).__init__(app, rootFrame, TablePosition.CONTROL, frameSide)

        # Create a table control frame in the parent control frame
        self.tableCtlFrame = tk.Frame(self.tkFrame)
        self.tableCtlFrame.pack(padx=0, pady=5, side=tk.BOTTOM)
        
        # Create a button to request a bidding hint
        tk.Button(self.tableCtlFrame, text='Hint', command=self.showHint).pack(side="left", padx=5)
        
        # Create a button to request another hand
        tk.Button(self.tableCtlFrame, text='Next Hand', command=self.app.table.nextHand).pack(side="left", padx=5)
        
        # Create a button to flush the log file
        tk.Button(self.tableCtlFrame, text='Flush Log', command=self.app.table.flushLog).pack(side="left", padx=5)

        
        # Create a frame for holding a text box 
        self.bidHintFrame = tk.Frame(self.tkFrame)
        self.bidHintFrame.pack(padx=0, pady=5, side=tk.BOTTOM)
        
        # Create a text box for displaying bid hints
        self.hintBox = tk.Text(self.bidHintFrame, height=25, width=40)
        self.hintBox.pack(pady=0)

        # Create a frame for holding buttons for entering a bid 
        self.bidEntryFrame = tk.Frame(self.tkFrame, highlightbackground='green', highlightthickness=2)
        self.bidEntryFrame.pack(padx=0, pady=5, side=tk.BOTTOM)

        self.bidLevel = tk.IntVar()
        self.bidLevel.set(BidLevels[0])  # default value
        levelSelect = tk.OptionMenu(self.bidEntryFrame, self.bidLevel, *BidLevels)
        levelSelect.pack(side=tk.LEFT, expand=True)

        self.bidSuit = tk.StringVar()
        self.bidSuit.set(BidSuits[0])  # default value
        suitSelect = tk.OptionMenu(self.bidEntryFrame, self.bidSuit, *BidSuits)
        suitSelect.pack(side=tk.LEFT, expand=True)


        # Button to enter the bid
        self.bidEnter = tk.Button(self.bidEntryFrame, text="Enter", fg="brown",
                                    command=self.bidSelectHandler)

        self.bidEnter.pack(side=tk.LEFT)
        
                
        # Create a frame to show the bids which have been made
        self.bidShowFrame = tk.Frame(self.tkFrame)
        self.bidShowFrame.pack(padx=0, pady=5, side=tk.TOP)
        self.bidRowIdx = 0
        self.bidColIdx = 0

        # Create labels for the bids table
        self.bidLabel = []

    def bidSelectHandler(self):
        level = self.bidLevel.get()
        suitStr = self.bidSuit.get()
        if suitStr == 'Club':
            suit = Suit.CLUB
        elif suitStr == 'Diamond':
            suit = Suit.DIAMOND
        elif suitStr == 'Heart':
            suit = Suit.HEART
        elif suitStr == 'Spade':
            suit = Suit.SPADE
        elif suitStr == 'NoTrump':
            suit = Suit.NOTRUMP
            
        # Tell the table the bid
        self.app.table.bidResponse(TablePosition.SOUTH, level, suit)
        
    '''
    This function displays a bidding hint when requested
    '''
    def showHint(self):
        table = self.app.table
        roundNum = table.roundNum
        humanPlayer = table.players[TablePosition.SOUTH]
        seat = humanPlayer.seat
        # Get the last bid by North
        northBid = table.bidsList[-2]
        if roundNum == 1:
            if seat <= 2:
                hintText = getHintForOpener()
            else:
                # Need to check if my partner bid
                bidIndex = seat - 3
                if table.bidsList[bidIndex][0] == 0:
                    # Partner passed
                    hintText = getHintForOpener()
                else:
                    hintText = getHintForResponder(northBid[0], northBid[1])
        elif roundNum == 2:
            if seat <= 2:
                hintText = getHintForOpenerRebid()
            else:
                # Need to check if my partner bid
                bidIndex = seat - 3
                if table.bidsList[bidIndex][0] == 0:
                    # Partner passed
                    hintText = getHintForOpenerRebid()
                else:
                    hintText = getHintForResponderRebid()
        else:
            hintText = "No hint available yet"

        self.hintBox.replace('1.0', '30.0', hintText)
        

    def createBidBoard(self, leadPos):
        pos = leadPos
        
        # Labels for header row
        label = tk.Label(self.bidShowFrame, text=pos.name, bg="green", fg="white")
        self.bidLabel.append(label)
        label.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        
        (pos, dummy) = getNextPosition(pos, leadPos)
        label = tk.Label(self.bidShowFrame, text=pos.name, bg="green", fg="white")
        self.bidLabel.append(label)
        label.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        
        (pos, dummy) = getNextPosition(pos, leadPos)
        label = tk.Label(self.bidShowFrame, text=pos.name, bg="green", fg="white")
        self.bidLabel.append(label)
        label.grid(row=0, column=2, sticky='w', padx=5, pady=5)

        (pos, dummy) = getNextPosition(pos, leadPos)
        label = tk.Label(self.bidShowFrame, text=pos.name, bg="green", fg="white")
        self.bidLabel.append(label)
        label.grid(row=0, column=3, sticky='w', padx=5, pady=5)


    def updateBids(self, table, position, bidLevel, bidSuit):
        #writeLog(table, "updateBids: lead=%s pos=%s lvl=%d suit=%s" % (table.leadPos, position, bidLevel, bidSuit))
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

        bidLabel = tk.Label(self.bidShowFrame, text=bidStr, bg="yellow", fg="black")
        bidLabel.grid(row=self.bidRowIdx, column=self.bidColIdx, sticky='w', padx=5, pady=5)
        
    def processHandDone(self):
        # Show the bid that should have been reached
        # TDB
        pass

    def nextHand(self):
        self.bidRowIdx = 0
        self.bidColIdx = 0
        # remove bid labels from the frame
        for label in self.bidShowFrame.grid_slaves():
            label.grid_forget()
            
        
