#!/home/richawil/Applications/anaconda3/bin/python

import os
import sys
import threading
from time import sleep
from enums import Suit, Level, PileOrder, TablePosition
from card import Card
from cardPile import CardPile
from deck import Deck
from cardTable import CardTable
# GUI Support
import tkinter as tk
from PIL import Image, ImageTk
from cardTableGui import CardTableGui
from frame import TableFrame
from controlFrame import ControlFrame


class Application(tk.Frame):
    def __init__(self, gameTable, masterFrame, masterWidth, masterHeight):
        super().__init__(masterFrame)
        self.masterFrame = masterFrame
        masterFrame.title("Card Table")

        self.table = gameTable
        self.cardTable = CardTableGui(self, masterWidth, masterHeight)        
        self.buildFrames(masterFrame, self.cardTable)
        gameTable.setGuiTable(self.cardTable)
        gameTable.startHand()

        
    def buildFrames(self, rootFrame, cardTable):
        # Create a control frame
        controlTableFrame = ControlFrame(self, rootFrame, tk.LEFT)
        cardTable.setFrameByPosition(TablePosition.CONTROL, controlTableFrame)

        # Create a west frame
        westTableFrame = TableFrame(self, rootFrame, TablePosition.WEST, tk.LEFT)
        cardTable.setFrameByPosition(TablePosition.WEST, westTableFrame)
        
        # Create a parent shared frame
        sharedFrame = tk.Frame(rootFrame, width=400, height=700, relief='raised')
        sharedFrame.pack(padx=0, pady=0, side=tk.LEFT)
        sharedFrame.pack_propagate(0)

        # Create a east frame
        eastTableFrame = TableFrame(self, rootFrame, TablePosition.EAST, tk.LEFT)
        cardTable.setFrameByPosition(TablePosition.EAST, eastTableFrame)
        
        # Create a south frame
        southTableFrame = TableFrame(self, sharedFrame, TablePosition.SOUTH, tk.BOTTOM)
        cardTable.setFrameByPosition(TablePosition.SOUTH, southTableFrame)

        # Create a center frame
        centerTableFrame = TableFrame(self, sharedFrame, TablePosition.CENTER, tk.BOTTOM)
        cardTable.setFrameByPosition(TablePosition.CENTER, centerTableFrame)
        
        # Create a north frame
        northTableFrame = TableFrame(self, sharedFrame, TablePosition.NORTH, tk.BOTTOM)
        cardTable.setFrameByPosition(TablePosition.NORTH, northTableFrame)

def thread_function(name, table):
    while not table.programDone:
        while not table.handDone:
            curPos = table.currentPos
            player = table.players[curPos]
            if not player.isHuman and table.outstandingBidReq:
                player.computerBidRequest(table.bidsList)
            sleep(1)
    sys.exit(0)


def main(argv):
    enableGui = argv[1] == 'True'
    humanPlaying = argv[2] == 'True'

    # Create a card table. This is the top level logic for a card game.
    table = CardTable(enableGui, humanPlaying)
    
    if enableGui:
        # Create the root widget, which is the application window
        rootFrame = tk.Tk()
        # Set the size of the main window
        rootFrame.geometry("1200x700")
        app = Application(table, rootFrame, 1200, 700)
        # Create a thread which simulate events from the computer
        thread = threading.Thread(target=thread_function, args=('Dealer', table))
        thread.start()
        app.mainloop()
    else:
        table.dealCards()
        table.findNextBidder()
        table.bidRequest()
        
    print("Program Done")
    
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage:")
        print("\tpython spades.py <enableGui> <humanPlaying>")
        print("\tExample")
        print("\tpython spades.py True True")
        exit(1)
    main(sys.argv)
