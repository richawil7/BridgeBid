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

        return (highCardPoints, distPoints)

    # Will return the higher of two tied suits
    def findLongestSuit(self):
        # Get the number of cards in each suit
        dist = {}
        dist[Suit.SPADE] = self.getNumCardsInSuit(Suit.SPADE)
        dist[Suit.HEART] = self.getNumCardsInSuit(Suit.HEART)
        dist[Suit.DIAMOND] = self.getNumCardsInSuit(Suit.DIAMOND)
        dist[Suit.CLUB] = self.getNumCardsInSuit(Suit.CLUB)

        # Find the suit with the most cards
        maxVal = 0
        maxSuit = Suit.ALL
        for value in range(Suit.SPADE.value, Suit.NOTRUMP.value):
            suit = Suit(value)
            if dist[suit] > maxVal:
                maxVal = dist[suit]
                maxSuit = suit
        return (maxVal, maxSuit)
        
    def numCardsInTwoLongestSuits(self):
        # Get the number of cards in each suit
        dist = {}
        dist[Suit.SPADE] = self.getNumCardsInSuit(Suit.SPADE)
        dist[Suit.HEART] = self.getNumCardsInSuit(Suit.HEART)
        dist[Suit.DIAMOND] = self.getNumCardsInSuit(Suit.DIAMOND)
        dist[Suit.CLUB] = self.getNumCardsInSuit(Suit.CLUB)

        # Find the 2 suits with the most cards
        maxVal1 = 0
        maxSuit1 = Suit.ALL
        for value in range(Suit.SPADE.value, Suit.NOTRUMP.value):
            suit = Suit(value)
            if dist[suit] > maxVal1:
                maxVal1 = dist[suit]
                maxSuit1 = suit
        maxVal2 = 0
        maxSuit2 = Suit.ALL
        for value in range(Suit.SPADE.value, Suit.NOTRUMP.value):
            suit = Suit(value)
            if suit == maxSuit1:
                continue
            if dist[suit] > maxVal2:
                maxVal2 = dist[suit]
                maxSuit2 = suit

        return (maxVal1, maxVal2)
        
    def evalSuitStrength(self, suit):
        numCardsInSuit = self.getNumCardsInSuit(suit)
        highCardCount = 0

        # Examine the top 4 cards, Ace, King, Queen, and Jack
        for i, value in enumerate(range(Level.Ace_HIGH.value, Level.Ten.value, -1)):
            level = Level(value)
            foundCard = self.hasCard(suit, level)
            if foundCard:
                highCardCount += 1

        return (numCardsInSuit, highCardCount)

    def isHandBalanced(self):
        # Get the number of cards in each suit
        dist = {}
        dist[Suit.SPADE] = self.getNumCardsInSuit(Suit.SPADE)
        dist[Suit.HEART] = self.getNumCardsInSuit(Suit.HEART)
        dist[Suit.DIAMOND] = self.getNumCardsInSuit(Suit.DIAMOND)
        dist[Suit.CLUB] = self.getNumCardsInSuit(Suit.CLUB)

        numDoubletons = 0
        for suit in Suit:
            if suit == Suit.ALL or suit == Suit.NOTRUMP:
                continue
            if dist[suit] < 2:
                return False
            if dist[suit] == 2:
                numDoubletons += 1
                if numDoubletons == 2:
                    return False
        return True

def evalSuitCategory(table, hand, suit):
    numCardsInSuit = hand.getNumCardsInSuit(suit)
    foundHole = False
    prevCardWasHigh = True
    highCardCount = 0
    
    # Examine the top 3 cards, Ace, King, and Queen
    hasAce = False
    hasKing = False
    hasQueen = False
    for i, value in enumerate(range(Level.Ace_HIGH.value, Level.Jack.value, -1)):
        level = Level(value)
        foundCard = hand.hasCard(suit, level)
        if foundCard:
            highCardCount += 1
            if i == 0:
                hasAce = True
            elif i == 1:
                hasKing = True
            elif i == 2:
                hasQueen = True
            if not prevCardWasHigh:
                foundHole = True
            prevCardWasHigh = True
        else:
            prevCardWasHigh = False
            
    if hasAce:
        if hasKing:
            category = SuitCategory.AKQ if hasQueen else SuitCategory.AKx
        else:
            category = SuitCategory.AxQ if hasQueen else SuitCategory.Axx
    else:
        if hasKing:
            category = SuitCategory.xKQ if hasQueen else SuitCategory.xKx
        else:
            category = SuitCategory.xxQ if hasQueen else SuitCategory.xxx

    writeLog(table, "Suit {} has {} cards, {} high cards, category {}\n".format(suit.name, numCardsInSuit, highCardCount, category.name))
    return (category, numCardsInSuit, highCardCount)
    
    # Return True if all 4 suits have stoppers
    def hasStoppers(self):
        for suit in Suit:
            if suit == Suit.ALL or suit == Suit.NOTRUMP:
                continue
            (category, numCardsInSuit, highCardCount) = evalSuitCategory(table, hand, suit)
            if category == SuitCategory.xxx:
                return False
            elif category == SuitCategory.xxQ:
                if numCardsInSuit < 3:
                    return False
            elif category == SuitCategory.xKx:
                if numCardsInSuit < 2:
                    return False
            elif category == SuitCategory.Axx:
                if numCardsInSuit < 2:
                    return False
            # All other categories have stoppers

        writeLog(table, "bridgeHand: hasStoppers in all suits")
        return True
