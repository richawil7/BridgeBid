'''
Player Class
A player in a card game
'''

from enums import Suit, Level
from cardPile import CardPile

class Player:

    def __init__(self, table, position, isHuman=False):
        self.table = table
        self.pos = position
        self.hand = CardPile()
        self.isHuman = isHuman
        
    def addCard(self, card):
        self.hand.addCard(card)
            
        
