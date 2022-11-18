'''
Deck Class

A deck of cards
'''

import random
from enums import Suit, Level, PileOrder
from cardPile import CardPile
from card import Card

class Deck(CardPile):

    def __init__(self):
        super(Deck, self).__init__(PileOrder.FIFO)
        for value in range(Suit.SPADE.value, Suit.CLUB.value + 1):
            suit = Suit(value)
            for level in Level:
                if level == Level.LOW or level == Level.Ace_LOW or level == Level.HIGH:
                    continue
                card = Card(suit, level)
                self.addCard(card)


    def shuffle(self):
        # Create a temporary pile
        tmpPile = CardPile(PileOrder.FIFO)

        # Sanity check. Deck should have 52 cards
        numCards = len(self.cards)
        if numCards != 52:
            print("ERROR: shuffle: deck has {} cards".format(len(self.cards)))
        assert numCards == 52
        
        for i in range(0, 52):
            # Randomly select a card from the deck
            index = random.randint(0, 51 - i)
            card = self.cards[index]
            # print("Round {}: index {} card {}".format(i, index, card.toStr()))

            # Transfer the card from the deck to the temporary file
            self.removeCard(card)
            tmpPile.addCard(card)

        # Repeat in the opposite direction
        for i in range(0, 52):
            # Randomly select a card from the temporary pile
            index = random.randint(0, 51 - i)
            card = tmpPile.cards[index]

            # Transfer the card from the temporary pile back to the deck
            tmpPile.removeCard(card)
            self.addCard(card)
