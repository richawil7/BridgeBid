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
    
        
    def getLoserCard(self, includeSpade=False):
        # Returns the lowest card in the longest (non-spade) suit
        lenLongestSuit = 0
        longestSuit = Suit.ALL
        if includeSpade:
            startSuit = Suit.SPADE
        else:
            startSuit = Suit.HEART
        for i in range(startSuit.value, Suit.CLUB.value + 1):
            suit = Suit(i)
            numInSuit = self.getNumCardsInSuit(suit)
            if numInSuit > lenLongestSuit:
                lenLongestSuit = numInSuit
                longestSuit = suit
        loserCard = self.findCardByPosition(longestSuit, CardPosition.LOWEST)
        return loserCard


    # This function finds the lowest card in this pile which would win over
    # all the cards in the given pile.
    # Example usage is that this pile is your bidding hand and the given
    # pile is the pile of played cards.
    def findLowestWinner(self, playedCards, suit):
        winnerCard = None
        for card in self.cards:
            if card.suit != suit:
                # Skip cards of different suits
                continue
            #print("findLowestWinner: evaluating %s from my hand" % card.toStr())
            isWinner = False
            for playedCard in playedCards.cards:
                if playedCard.suit != suit:
                    # Skip cards of different suits
                    continue
                if card.level.value > playedCard.level.value:
                    # print("findLowestWinner: %s is a winner" % card.toStr())
                    isWinner = True
                    if winnerCard == None:
                        # print("findLowestWinner: saving %s as a winner" % card.toStr())
                        winnerCard = card
                    else:
                        # Check if this card is lower than the existing winner
                        if card.level.value < winnerCard.level.value:
                            # print("findLowestWinner: saving %s as a lower winner" % card.toStr())
                            winnerCard = card
                            
        if winnerCard != None:
            print("findLowestWinner: returning %s as a winner" % winnerCard.toStr())
            pass
        else:
            print("findLowestWinner: no winner found")
            pass
        
        return winnerCard

    # This function finds the highest card in this pile which would lose 
    # over all the cards in the given pile.
    # Example usage is that this pile is your bidding hand and the given
    # pile is the pile of played cards.
    def findHighestLoser(self, playedCards, suit):
        loserCard = None
        for card in self.cards:
            if card.suit != suit:
                # Skip cards of different suits
                continue
            #print("findHighesLoser: evaluating %s from my hand" % card.toStr())
            isLoser = False
            for playedCard in playedCards.cards:
                if playedCard.suit != suit:
                    # Skip cards of different suits
                    continue
                if card.level.value < playedCard.level.value:
                    # print("findHighestLoser: %s is a loser" % card.toStr())
                    isLoser = True
                    if loserCard == None:
                        # print("findHighestLoser: saving %s as a loser" % card.toStr())
                        loserCard = card
                    else:
                        # Check if this card is higher than the existing loser
                        if card.level.value > loserCard.level.value:
                            # print("findHighestLoser: saving %s as a higher loser" % card.toStr())
                            loserCard = card
        return loserCard
    
    
    # Returns a card from the spades hand of the specified card category.
    # includeTrump indicates whether this function will allow a return of a Spade
    def findCardByCategory(self, category, spadesBroken, includeTrump=False):
        for card in self.cards:
            if not spadesBroken and card.suit == Suit.SPADE:
                continue
            
            if card.initialCategory == category:
                if card.suit == Suit.SPADE:
                    if includeTrump:
                        return card
                else:
                    return card
        return None

    def findHighCardWinner(self, spadesBroken):
        for card in self.cards:
            if not spadesBroken and card.suit == Suit.SPADE:
                continue
    
            if card.initialCategory == CardCategory.HighCard:
                if card.count <= 0:
                    return card
        return None
        
