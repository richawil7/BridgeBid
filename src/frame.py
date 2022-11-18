'''
Frame Class

A class representing a frame within a card table.
This class is independent of the type of card game.
It is mostly a GUI helper, setting up frames for each player and a 
center frame for showing played cards.
'''

import tkinter as tk
from enums import TablePosition
from constants import *

class TableFrame():

    def __init__(self, app, rootFrame, position, frameSide):
        if position == TablePosition.CONTROL:
            self.tkFrame = tk.Frame(rootFrame, width=300, height=700, relief='raised', borderwidth=5)
        elif position == TablePosition.WEST or position == TablePosition.EAST:
            self.tkFrame = tk.Frame(rootFrame, width=200, height=700, highlightbackground='yellow', highlightthickness=2)
        elif position == TablePosition.NORTH or position == TablePosition.SOUTH:
            self.tkFrame = tk.Frame(rootFrame, width=400, height=210, highlightbackground='green', highlightthickness=2)
        elif position == TablePosition.CENTER:
            self.tkFrame = tk.Frame(rootFrame, width=400, height=250, relief='raised', borderwidth=5)
        else:
            print("Invalid position {}".format(position.name))
        self.tkFrame.pack(padx=5, pady=5, side=frameSide)
        self.tkFrame.pack_propagate(0)

        self.app = app
        self.pos = position
        self.canvas = None
        #self.cardPile = None
        #self.cardDescList = []
        self.createSubFrames(app.cardTable.cardSelectHandler)
        self.createLabels()

    def clear(self):
        if self.canvas != None:
            if self.pos == TablePosition.NORTH or \
               self.pos == TablePosition.EAST or \
               self.pos == TablePosition.SOUTH or \
               self.pos == TablePosition.WEST or \
               self.pos == TablePosition.CONTROL:
                   self.canvas.delete("all")

    def draw_frame(self):
        #self.clear()
        self.displayCards()

    
    def createSubFrames(self, cardHandler):
        if self.pos == TablePosition.WEST or self.pos == TablePosition.EAST:
            botFrame = tk.Frame(self.tkFrame, width=200, height=150)
            botFrame.pack(side=tk.BOTTOM)
            self.canvas = tk.Canvas(self.tkFrame, width=200, height=380, highlightbackground='black', highlightthickness=2)
            self.canvas.pack(side=tk.BOTTOM)
            self.canvas.bind('<Button-1>', cardHandler)
        elif self.pos == TablePosition.NORTH or self.pos == TablePosition.SOUTH:
            self.canvas = tk.Canvas(self.tkFrame, width=400, height=150, highlightbackground='black', highlightthickness=2)
            self.canvas.pack(side=tk.BOTTOM)
            self.canvas.bind('<Button-1>', cardHandler)
        elif self.pos == TablePosition.CENTER:
            self.canvas = tk.Canvas(self.tkFrame, width=400, height=250)
            self.canvas.pack()
        
    def createLabels(self):
        if self.pos == TablePosition.CENTER or self.pos == TablePosition.CONTROL:
            # No labels on the center or control frame
            return
        #print("Enum={} name={} value={}".format(pos, pos.name, pos.value))
        label = tk.Label(self.tkFrame, text=self.pos.name, bg="green", fg="white")
        label.pack(padx=20, pady=20, side=tk.TOP)


    def displayCards(self):
        # Find the card pile for this frame
        if self.pos == TablePosition.CENTER:
            self.cardPile = self.app.table.cardsPlayed
        else:
            self.cardPile = self.app.table.players[self.pos].hand
        for card in self.cardPile.cards:
            anchor_x = card.anchor[0]
            anchor_y = card.anchor[1]
            if TablePosition.NORTH == self.pos or \
               TablePosition.SOUTH == self.pos:
                cardImage = card.getCardImage(0)
            elif TablePosition.EAST == self.pos or \
                 TablePosition.WEST == self.pos:
                cardImage = card.getCardImage(90)
            else:
                cardImage = card.getCardImage(0)
            self.canvas.create_image(anchor_x, anchor_y, image=cardImage, anchor='nw')
            
