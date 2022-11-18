'''
Card Pile Class

A collection of cards
'''

from enums import Suit, Level, PileOrder, PileDisplayMode, CardPosition
from utils import *
from frame import TableFrame

class CardPile:

    def __init__(self, faceUp=False, order=PileOrder.LIFO, mode=PileDisplayMode.NONE):
        self.cards = []
        self.order = order
        self.faceUp = faceUp
        self.displayMode = mode

    def copy(self):
        # This is a copy constuctor
        newPile = CardPile(self.order, self.displayMode)
        newPile.cards = self.cards.copy()
        self.faceUp = False
        return newPile

    def setDisplayMode(self, mode):
        self.displayMode = mode
        
    def addCard(self, addCard, order=None):
        if order == None:
            order = self.order
        if order == PileOrder.FIFO:
            self.cards.append(addCard)
        else:
            self.cards.insert(0, addCard)
        
    def hasCard(self, suit, level):
        for card in self.cards:
            if card.suit == suit and card.level == level:
                return True
        return False

    # Try to delete a card. Return the card if found, else return None.
    def deleteCard(self, suit, level):
        for card in self.cards:
            if card.suit == suit and card.level == level:
                self.cards.remove(card)
                return card
        return None

    def findCardByValue(self, suit, level):
        for card in self.cards:
            if card.level == level and card.suit == suit:
                return card
        return None
    
    def findCardByPosition(self, suit, position, excludeSpade=False):
        highestCardLevel = Level.LOW
        highestCard = None
        lowestCardLevel = Level.HIGH
        lowestCard = None

        # Figure out if the pile has nothing but spades left
        numSpades = self.getNumCardsInSuit(Suit.SPADE)
        onlySpades = (len(self.cards) == numSpades)
        
        for card in self.cards:
            if suit != Suit.ALL:
                # Skip cards which are not in the desired suit
                if card.suit != suit:
                    continue
            elif excludeSpade and card.suit == Suit.SPADE:
                continue        
            else:
                # In general, we want to avoid returning a
                # low spade. But if all we have is spades left
                # we need to choose one
                if position == CardPosition.LOWEST and \
                   card.suit == Suit.SPADE and \
                   not onlySpades:
                    continue
                
            if card.level.value > highestCardLevel.value:
                highestCardLevel = card.level
                highestCard = card
            if card.level.value < lowestCardLevel.value:
                lowestCardLevel = card.level
                lowestCard = card
        if position == CardPosition.LOWEST:
            return lowestCard
        if position == CardPosition.HIGHEST:
            return highestCard
                
    def removeCardByPosition(self, suit, position):
        card = self.findCardByPosition(suit, position)
        # print("Found card {}".format(card.toStr()))
        if card != None:
            self.cards.remove(card)
        else:
            #print("removeCardByPosition: suit {} pos {} not found\n".format(suit.name, position.name))
            pass
        return card

    def removeCard(self, delCard):
        self.cards.remove(delCard)
        
    def selectCard(self):
        if self.order == PileOrder.FIFO:
            card = self.cards.pop(0)
        else:
            card = self.cards.pop()
        return card

    def getNumCards(self):
        return len(self.cards)

    def getNumCardsInSuit(self, suit):
        count = 0
        for card in self.cards:
            if card.suit == suit:
                count += 1
        return count

    def getCardByIndex(self, suit, index):
        # This function returns the indexth card for the given suit
        # Index = 0 will return the first card in the hand of the given suit
        # None is returned if the suit or matching index is not found
        count = 0
        for card in self.cards:
            if card.suit == suit:
                if count == index:
                    return card
                count += 1
        return None

    # This function returns a boolean indicating if a card of a given suit
    # is in this card pile
    def hasSuit(self, suit):
        for card in self.cards:
            if card.suit == suit:
                return True
        return False


    # This function returns a boolean indicating whether this card pile
    # includes a high card (Ace, King, or Queen) in a given suit.
    def hasHighCard(self, suit):
        for card in self.cards:
            if card.suit == suit and card.level.value >= 12:
                return True
        return False
        
    # This function checks if the given card is higher than all the other
    # cards in this pile. Only considers cards in the pile which are the same
    # suit as the given card. Returns True if given card is higher than all
    # other cards of the same suit.
    def isHighestCard(self, highCard):
        for card in self.cards:
            if card.suit != highCard.suit:
                # Skip cards of different suits
                continue
            if card.level.value > highCard.level.value:
                return False
        return True

    def sort(self):
        # This function sorts a pile first by suit, and then within the
        # suit by level
        spades = []
        hearts = []
        diamonds = []
        clubs = []
        for card in self.cards:
            if card.suit == Suit.SPADE:
                spades.append(card)
            elif card.suit == Suit.HEART:
                hearts.append(card)
            elif card.suit == Suit.DIAMOND:
                diamonds.append(card)
            elif card.suit == Suit.CLUB:
                clubs.append(card)
        spades.sort(key=lambda x: x.level.value, reverse=True)
        hearts.sort(key=lambda x: x.level.value, reverse=True)
        diamonds.sort(key=lambda x: x.level.value, reverse=True)
        clubs.sort(key=lambda x: x.level.value, reverse=True)
        self.cards = spades + hearts + diamonds + clubs
        
    def show(self):
        for card in self.cards:
            card.show()


    # GUI Methods
    def findCardByPoint(self, x, y):
        # Get the hand position by looking at a card
        if len(self.cards) == 0:
            return None
        card = self.cards[0]
        if not isPointInCardField(card.position, x, y):
            print("Point is not in card field")
            return None
        for idx, card in enumerate(self.cards):
            # Define the boundries in which card images can live
            x_left = card.anchor[0]
            x_right = card.anchor[0] + CARD_PIXEL_WIDTH
            y_top = card.anchor[1]
            y_bottom = card.anchor[1] + CARD_PIXEL_HEIGHT
            # The right boundary needs to be adjusted if the next card
            # overlaps it
            if idx + 1 < len(self.cards):
                nextCard = self.cards[idx + 1]
                nextCard_x_left = nextCard.anchor[0]
                if nextCard_x_left < x_right:
                    x_right = nextCard_x_left
            #print("Card boundries x_left={} x_right={} y_top={} y_bottom={}".format(x_left, x_right, y_top, y_bottom))            
            if x >= x_left and x <= x_right and y <= y_bottom and y >= y_top:
                return card
        return None

                
    def setGuiParams(self, tableGui, tablePosition):
        anchorCenter = getAnchorPointByPosition(tablePosition)
        anchor_x = anchorCenter[0]
        anchor_y = anchorCenter[1]
        tableFrame = tableGui.getFrameByPosition(tablePosition)
        for card in self.cards:
            if TablePosition.NORTH == tablePosition:
                card.setGuiParams(tableFrame.canvas, anchor_x, anchor_y)
                anchor_x += CARD_PIXEL_OFFSET
            if TablePosition.SOUTH == tablePosition:
                card.setGuiParams(tableFrame.canvas, anchor_x, anchor_y)
                anchor_x += CARD_PIXEL_OFFSET
            elif TablePosition.EAST == tablePosition or \
               TablePosition.WEST == tablePosition: 
                card.setGuiParams(tableFrame.canvas, anchor_x, anchor_y)
                anchor_y += CARD_PIXEL_OFFSET
            
    @staticmethod
    def setCenterGuiParams(table, posToCardMap):
        tableFrame = table.getFrameByPosition(TablePosition.CENTER)
        # Turn the dictionary of posToCardMap into a list
        cardTupleList = posToCardMap.items()
        for cardTuple in cardTupleList:
            pos = cardTuple[0]
            card = cardTuple[1]
            #print("Position:{} Card:{}".format(pos.name, card.toStr()))
            if pos == TablePosition.NORTH:
                anchor_x = 170
                anchor_y = 7
            elif pos == TablePosition.EAST:
                anchor_x = 270
                anchor_y = 77
            elif pos == TablePosition.SOUTH:
                anchor_x = 170
                anchor_y = 147
            elif pos == TablePosition.WEST:
                anchor_x = 70
                anchor_y = 77
                
            card.setGuiParams(tableFrame.canvas, anchor_x, anchor_y, True)
