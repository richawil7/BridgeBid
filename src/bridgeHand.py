'''
A Bridge Hand Class

A collection of bridgeCards
'''

from enums import *
from utils import *
from cardPile import CardPile

class BridgeHand(CardPile):

    def __init__(self, pos):
        cardsFaceUp = False
        if pos == TablePosition.SOUTH:
            cardsFaceUp = True
        super(BridgeHand, self).__init__(faceUp=cardsFaceUp)

    def evalHand(self, distMethod):
        # Calculate high card points
        highCardPoints = 0
        for card in self.cards:
            if card.level.value >= Level.Jack.value:
                highCardPoints += card.level.value - Level.Ten.value

        # Calculate distribution points
        distPoints = 0
        for suit in Suit:
            if distMethod == DistMethod.LONG:
                numCardsInSuit = self.getNumCardsInSuit(suit)
                if numCardsInSuit > 4:
                    distPoints += numCardsInSuit - 4
            elif distMethod == DistMethod.SHORT:
                if numCardsInSuit < 3:
                    distPoints += 3 - numCardsInSuit

        return highCardPoints + distPoints
        
