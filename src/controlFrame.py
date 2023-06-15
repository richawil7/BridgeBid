'''
Control Frame Class

A class representing the control frame within a card table.
This class is somewhat dependent of the type of card game, as it will
show game control widgets and game status (e.g. player's scores).
'''

import tkinter as tk
from infoLog import Log
from enums import TablePosition, Suit, PlayerRole
from frame import TableFrame
from bidNode import *
from bidNotif import BidNotif
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
        
        # Create a button to request another hand
        tk.Button(self.tableCtlFrame, text='Next Hand', command=self.app.table.nextHand).pack(side="left", padx=5)
        
        # Create a button to flush the log file
        tk.Button(self.tableCtlFrame, text='Flush Log', command=Log.flush).pack(side="left", padx=5)

        
        # Create a frame for holding a text box 
        self.bidHintFrame = tk.Frame(self.tkFrame)
        self.bidHintFrame.pack(padx=0, pady=5, side=tk.BOTTOM)
        
        # Create a text box for displaying bid hints
        self.hintBox = tk.Text(self.bidHintFrame, height=25, width=40)
        self.hintBox.pack(pady=0)

        # Create a frame for holding buttons for requesting hints
        self.bidHintFrame = tk.Frame(self.tkFrame, highlightbackground='red', highlightthickness=2)
        self.bidHintFrame.pack(padx=0, pady=5, side=tk.BOTTOM)
        
        # Create buttons to request a bidding hints
        tk.Button(self.bidHintFrame, text='Means', command=self.showHint0).pack(side="left", padx=5)        
        tk.Button(self.bidHintFrame, text='Hint1', command=self.showHint1).pack(side="left", padx=5)
        tk.Button(self.bidHintFrame, text='Hint2', command=self.showHint2).pack(side="left", padx=5)
        tk.Button(self.bidHintFrame, text='Hint3', command=self.showHint3).pack(side="left", padx=5)
        
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
        bidStr = getBidStr(level, suit)
            
        # Tell the table the bid
        table = self.app.table
        player = table.players[TablePosition.SOUTH]
        
        # Use the notification built by the computer
        bidNotif = player.lastNotif
        # Check if the computer and human agreed on this bid
        if level != 0 or bidNotif.bid[0] != 0:
            if level != bidNotif.bid[0] or suit != bidNotif.bid[1]:
                computerBidStr = getBidStr(bidNotif.bid[0], bidNotif.bid[1])
                print("Computer bid %s != Human bid %s" % (computerBidStr, bidStr))
                # Overwrite the last bid with what the human bid
                bidNotif.bid = (level, suit)
        self.app.table.bidResponse(TablePosition.SOUTH, bidNotif)
        
    '''
    This function displays a bidding hint when requested
    '''
    def getBidNode(self):
        table = self.app.table
        humanPlayer = table.players[TablePosition.SOUTH]
        return humanPlayer.bidNode

    def showHint0(self):
        bidNode = self.getBidNode()
        hintText = bidNode.interpret
        self.hintBox.replace('1.0', '30.0', hintText.expandtabs(2))

    def showHint1(self):
        bidNode = self.getBidNode()
        hintText = bidNode.bidHints[0]
        self.hintBox.replace('1.0', '30.0', hintText.expandtabs(2))
        
    def showHint2(self):
        bidNode = self.getBidNode()
        hintText = bidNode.bidHints[1]
        self.hintBox.replace('1.0', '30.0', hintText.expandtabs(2))
        
    def showHint3(self):
        bidNode =self. getBidNode()
        hintText = bidNode.bidHints[2]
        self.hintBox.replace('1.0', '30.0', hintText.expandtabs(2))
        

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
        # Clear the hint text box
        self.hintBox.delete('1.0', '30.0')
        
        # remove bid labels from the frame
        for label in self.bidShowFrame.grid_slaves():
            label.grid_forget()
            
        # Reset the bid selection
        self.bidLevel.set(BidLevels[0])
        self.bidSuit.set(BidSuits[0])
