'''
Functions used for generating bids
'''

from enums import Suit, Level, DistMethod, PlayerRole
from utils import *
from card import Card
from cardPile import CardPile

def findLargestBid(table):
    bidsList = table.bidsList
    # Find the largest bid in the list
    maxLevel = 0
    maxSuit = Suit.CLUB
    for bid in bidsList:
        if bid[0] > maxLevel:
            maxLevel = bid[0]
            maxSuit = bid[1]            
        elif bid[0] == maxLevel:
            if bid[1].value > maxSuit.value:
                maxSuit = bid[1]
    bidStr = getBidStr(maxLevel, maxSuit)
    print("Largest bid is %s" % bidStr)
    return (maxLevel, maxSuit)

def stubBid(table, bidsList):
    # Get the largest bid
    largestBid = findLargestBid(table)
    lastBidLevel = largestBid[0]
    lastBidSuit = largestBid[1]
    
    if lastBidLevel == 0:
        # Pass
        nextBidLevel = 1
        nextBidSuit = Suit.CLUB
    else:
        nextBidLevel = lastBidLevel
        if lastBidSuit == Suit.NOTRUMP:
            nextBidLevel = lastBidLevel + 1
            nextBidSuit = Suit.CLUB
        elif lastBidSuit == Suit.SPADE:
            nextBidSuit = Suit.NOTRUMP
        elif lastBidSuit == Suit.HEART:
            nextBidSuit = Suit.SPADE
        elif lastBidSuit == Suit.DIAMOND:
            nextBidSuit = Suit.HEART
        elif lastBidSuit == Suit.CLUB:
            nextBidSuit = Suit.DIAMOND
    bidStr = getBidStr(nextBidLevel, nextBidSuit)
    writeLog(table, "stubBid: %s in round %d by %s\n" % (bidStr, table.roundNum, table.currentPos.name))
    return (nextBidLevel, nextBidSuit)


def whosMyPartner(myPos):
    if myPos == TablePosition.NORTH:
        return TablePosition.SOUTH
    elif myPos == TablePosition.EAST:
        return TablePosition.WEST
    elif myPos == TablePosition.SOUTH:
        return TablePosition.NORTH
    elif myPos == TablePosition.WEST:
        return TablePosition.EAST

    
def getMyPlayerRole(table, player):
    # Does the table already have an opener?
    hasOpener = table.hasOpener
    # Have both teams bid?
    competition = table.competition
    # What seat is the player sitting in?
    seat = player.seat
    
    # Determine this player's bidding role
    if not hasOpener and not competition:
        # No one has opened yet
        iCanOpen = canIOpen(player.hand, competition, seat) 
        if iCanOpen:
            return PlayerRole.OPENER

    elif not hasOpener and competition:
        print("bidUtils: getMyPlayerRole: Error-invalid state ")

    elif hasOpener:
        # Check if my partner was the opener
        if len(table.bidsList) >= 2:
            if seat >= 3:
                partnerBidIdx = seat - 2 - 1
            else:
                partnerBidIdx = 4 + seat - 2 - 1
            partnerBid = table.bidsList[partnerBidIdx][0]
            if partnerBid > 0:
                # My partner opened
                if table.roundNum == 1:
                    writeLog(table, "bidUtils: getMyPlayerRole: partner opened\n")
                return PlayerRole.RESPONDER
            else:
                # My partner passed
                writeLog(table, "bidUtils: getMyPlayerRole: partner passed\n")
        else:
            iCanOpen = canIOpen(player.hand, competition, seat) 
            if iCanOpen:
                return PlayerRole.OPENER

    return PlayerRole.UNKNOWN

# This function takes the bid list from the table and extracts only the
# bids for the partnership to which the player belongs
def getTeamBidSequence(table, playerPos):
    bidSeq = []
    currentPos = table.leadPos
    partnerPos = whosMyPartner(playerPos)
    for bid in table.bidsList:
        if currentPos == playerPos or currentPos == partnerPos:
            bidSeq.append(bid)
        (currentPos, dummy) = getNextPosition(currentPos, table.leadPos)
    return bidSeq


def canIOpen(hand, competition, seatNum):
    (hcPts, lenPts) = hand.evalHand(DistMethod.HCP_LONG)
    totalPts = hcPts + lenPts 
    if totalPts >= 14:
        return True

    # Get number of cards in the longest 2 suits
    (suit1, numCardsLongest, suit2, numCardsNextLongest) = hand.numCardsInTwoLongestSuits()

    # Can open with the rule of 20
    if hcPts + numCardsLongest + numCardsNextLongest >= 20:
        return True

    # Check if we can open due to length
    # Find the longest suit
    (numCards, longestSuit) = hand.findLongestSuit()
    if numCards < 6:
        return False

    if longestSuit == Suit.CLUB:
        return False
    
    # Check the strength of the longest suit
    (numCards, numHighCards) = hand.evalSuitStrength(longestSuit)
    if numHighCards <= 1:
        return False

    # Check the number of cards in the next longest suit
    if numCardsNextLongest >= 4:
        return False

    return True
    
def findLongerMinor(hand):
    numDiamonds = hand.getNumCardsInSuit(Suit.DIAMOND)
    numClubs = hand.getNumCardsInSuit(Suit.CLUB)
    if numDiamonds > numClubs:
        return Suit.DIAMOND
    elif numClubs > numDiamonds:
        return Suit.CLUB
    elif numDiamonds == 4:
        return Suit.DIAMOND
    elif numClubs == 3:
        return Suit.CLUB
