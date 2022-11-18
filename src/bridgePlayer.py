'''
Bridge Player Class
A player of the game of Spades
'''

from enums import Suit, Level
from utils import *
from cardPile import CardPile
from player import Player
from bridgeHand import BridgeHand
import bid

class BridgePlayer(Player):

    def __init__(self, table, position, isHuman=False):
        super(BridgePlayer, self).__init__(table, position, isHuman)
        self.outstndCards = {Suit.SPADE: 0, Suit.HEART: 0, Suit.DIAMOND: 0, Suit.CLUB : 0}
        self.distribution = {Suit.SPADE : 0, Suit.HEART : 0, Suit.DIAMOND : 0, Suit.CLUB : 0}
        self.hand = BridgeHand(position)


    def initOutstndCards(self, hand):
        self.outstndCards[Suit.SPADE] = 13
        self.outstndCards[Suit.HEART] = 13
        self.outstndCards[Suit.DIAMOND] = 13
        self.outstndCards[Suit.CLUB] = 13
        # Remove from the card count cards in my own hand
        for card in hand.cards:
            self.updateOutstndCards(card)
            
        
    def updateOutstndCards(self, card):
        if card.suit == Suit.SPADE:
            self.outstndCards[Suit.SPADE] -= 1
        elif card.suit == Suit.HEART:
            self.outstndCards[Suit.HEART] -= 1
        elif card.suit == Suit.DIAMOND:
            self.outstndCards[Suit.DIAMOND] -= 1
        elif card.suit == Suit.CLUB:
            self.outstndCards[Suit.CLUB] -= 1

    def calcBid(self):
        handBid = bid.calcBid(self.table, self.hand, self.biddingHand, self.distribution, self.bidStats)

        handStr = getHandStr(self.hand)
        print("%s \t%s  Dist=%d%d%d%d  Hi/Ruff/Long/Duck=%d/%d/%d/%d" % \
              (self.pos.name, \
               handStr, \
               self.distribution[Suit.SPADE], \
               self.distribution[Suit.HEART], \
               self.distribution[Suit.DIAMOND], \
               self.distribution[Suit.CLUB], \
               self.bidStats[CardCategory.HighCard], \
               self.bidStats[CardCategory.Ruff], \
               self.bidStats[CardCategory.Long], \
               self.bidStats[CardCategory.Duck] \
              ) \
             )
      
        return handBid
        
    def bidRequest(self, listOfBids):
        if self.isHuman:
            if self.table.guiEnabled:
                #print("Pick a card to play by clicking on it")
                bidLevel = int(input("Enter the bid level"))
                suitStr = input("Enter the suit")
                if suitStr == "C":
                    bidSuit = Suit.CLUB
                elif suitStr == "D":
                    bidSuit = Suit.DIAMOND
                elif suitStr == "H":
                    bidSuit = Suit.HEART
                elif suitStr == "S":
                    bidSuit = Suit.SPADE
                elif suitStr == "N":
                    bidSuit = Suit.NOTRUMP
                else:
                    bidSuit = Suit.NOTRUMP
                self.table.bidResponse(self.pos, bidLevel, bidSuit)

            else:
                print("Pick a card to play")
                self.hand.show()
                numStr = input("Enter number of card (counting from 1)")
                index = int(numStr)
                card = self.hand.cards[index-1]
                print("You selected card {}".format(card.toStr()))
                self.hand.removeCard(card)
                self.table.cardPlayed(card)      
            # Thread will respond with a card played by computer
            
        
    def computerBidRequest(self, bidsList):
        # writeLog(self.table, "bridgePlayer: computerSelectACard: position %s  lead %s\n" % (self.pos.name, self.table.leadPos.name))
        print("bridgePlayer: computerSelectACard: position %s  lead %s\n" % (self.pos.name, self.table.leadPos.name))
        if len(bidsList) > 0:
            print("List of bids so far: %s" % bidsList)
            bidTuple = bidsList[-1]
            lastBidLevel = bidTuple[0]
            nextBidLevel = lastBidLevel + 1
            lastBidSuit = bidTuple[1]
            print("Last bid was %d of %s" % (lastBidLevel, lastBidSuit.name))
            if lastBidSuit == Suit.NOTRUMP:
                nextBidSuit = Suit.CLUB
            elif lastBidSuit == Suit.HEART:
                nextBidSuit = Suit.SPADE
            else:
                nextBidSuit = Suit.HEART
        else:
            # First bid
            nextBidLevel = 1
            nextBidSuit = Suit.CLUB
            
        self.table.bidResponse(self.pos, nextBidLevel, nextBidSuit)
        

    '''
    This function is called by the card table at the end of each round.
    The player updates the duck count for high cards.
    The outstanding card counts are also adjusted.
    '''
    def processRoundDone(self, leadPosition, winningPosition, wasTrumped):
        # Get the cards that were played for this round
        cardsPlayed = self.table.cardsPlayed.cards
        # Returns cards played starting with lead position
        currentPos = leadPosition
        # print("processRoundDone: I am %s leader was %s" % (self.pos.name, leadPosition.name))
        for card in cardsPlayed:
            if currentPos != self.pos:
                # This is a card played by an opponent
                # Adjust the outstanding card count
                self.updateOutstndCards(card)
            else:
                # This is the card this player played.
                # Did this player win this round?
                if self.pos == winningPosition:
                    card.finalCategory = CardCategory.Winner
                else:
                    card.finalCategory = CardCategory.Loser
                    
            (currentPos, dummy) = getNextPosition(currentPos, leadPosition)
            
            # Was the played card a high card?
            if card.level.value > Level.Jack.value:
                # Is there a card in my bidding hand which is:
                # the same suit and
                # is a high card which is lower than this played card
                # then reduce the duck count
                for bidCard in self.biddingHand.cards:
                    if card.suit == bidCard.suit and \
                       bidCard.level.value > Level.Jack.value and \
                       bidCard.level.value < card.level.value:
                        bidCard.count -= 1
                        # print("%s reduced duck count for card %s to %d" % (self.pos.name, bidCard.toStr(), bidCard.count))

        # Check if this round was trumped
        if wasTrumped:
            # All cards in the bidding hand of the led suit are now losers
            for bidCard in self.biddingHand.cards:
                if bidCard.suit == cardsPlayed[0].suit:
                    bidCard.currentCategory = CardCategory.Loser
            
        # Check for suits with no outstanding cards
        for suit in Suit:
            if suit == Suit.ALL:
                continue
            if self.outstndCards[suit] == 0:
                if suit == Suit.SPADE:
                    # My opponents no longer have spades
                    # All the spades in this player's bidding hand are winners
                    for bidCard in self.biddingHand.cards:
                        if bidCard.suit == Suit.SPADE:
                            bidCard.currentCategory = CardCategory.Winner

        #self.showHandStatus()
        self.evalHandState()
        
    '''
    This function is called by the card table at the end of a hand
    '''
    def processHandDone(self):
        # Turn all the cards face up
        if self.pos == TablePosition.SOUTH:
            return
        for card in self.hand.cards:
            card.faceUp = True

    '''
    This function is called by the card table to prepare for the next hand
    '''
    def nextHand(self):
        # Turn all the card face down
        for card in self.hand.cards:
            card.faceUp = False
            
        # Return all the cards to the deck
        self.table.deck.cards.extend(self.hand.cards)
        del self.hand.cards[:]
        
        
