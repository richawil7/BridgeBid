'''
Functions used for generating bids
'''

from infoLog import Log
from enums import Suit, Level, DistMethod, PlayerRole
from utils import *
from card import Card
from cardPile import CardPile

# Find the largest bid at the table
def findLargestTableBid(table):
    bidsList = table.bidsList
    return findLargestBid(bidsList)

# Find the largest bid by my team
def findLargestTeamBid(player):
    bidsList = player.teamState.bidSeq
    return findLargestBid(bidsList)

# Find the largest bid in a sequence of bids
def findLargestBid(bidsList):
    # Find the largest bid in the list
    maxLevel = 0
    maxSuit = Suit.CLUB
    for bid in bidsList:
        if bid[0] > maxLevel:
            maxLevel = bid[0]
            maxSuit = bid[1]            
        elif bid[0] == maxLevel:
            if bid[1].value < maxSuit.value:
                maxSuit = bid[1]
    bidStr = getBidStr(maxLevel, maxSuit)
    return (maxLevel, maxSuit)


# Given a proposed suit, find the lowest allowed level at which the suit
# can be bid
def getNextLowestBid(table, suit):
    # Find the highest bid on the table so far
    (maxLevel, maxSuit) = findLargestTableBid(table)
    if suit.value < maxSuit.value:
        # Can bid proposed suit at current level
        return maxLevel
    else:
        # Must bid the suit at the next higher level
        if maxLevel < 6:
            return maxLevel + 1
        else:
            return 0

    
# Given a suit and a number of total points for the team,
# returns a recommended bid level
def getBidLevel(teamPoints, suit):
    if teamPoints < 20:
        return 0
    elif teamPoints < 22:
        return 1
    elif teamPoints < 24:
        return 2
    elif teamPoints < 26:
        return 3
    elif teamPoints < 29:
        if isMinor(suit):
            return 3
        else:
            return 4 
    elif teamPoints < 32:
        return 5
    elif teamPoints < 35:
        return 6
    return 7

# Returns the range of points implied by a bid
# Only call this function when making a natural bid
def getPointRange(player, bidSuit):
        if player.playerRole == PlayerRole.RESPONDER:
            (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
            totalPts = hcPts + distPts
            if bidSuit == Suit.NOTRUMP:
                if totalPts >= 0 and totalPts <= 6:
                    return (0, 6)
                elif totalPts >= 7 and totalPts <= 8:
                    return (7, 8)
                elif totalPts >= 9 and totalPts <= 12:
                    return (9, 12)
                elif totalPts >= 13:
                    return (13, totalPts)
            else:
                # A suit bid
                if totalPts >= 0 and totalPts <= 5:
                    return (0, 5)
                elif totalPts >= 6 and totalPts <= 9:
                    return (6, 9)
                elif totalPts >= 10 and totalPts <= 12:
                    return (10, 12)
                elif totalPts >= 13:
                    return (22, totalPts)
        else:
            # I am the opener, or the would-be opener
            (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_LONG)
            totalPts = hcPts + distPts
            if bidSuit == Suit.NOTRUMP:
                if totalPts >= 15 and totalPts <= 17:
                    return (15, 17)
                elif totalPts >= 18 and totalPts <= 19:
                    return (18, 19)
                elif totalPts >= 20 and totalPts <= 21:
                    return (20, 21)
                elif totalPts >= 22 and totalPts <= 24:
                    return (22, 24)
                elif totalPts >= 25 and totalPts <= 27:
                    return (25, 27)
                elif totalPts >= 28:
                    return (28, totalPts)
            else:
                # A suit bid
                if totalPts >= 0 and totalPts <= 12:
                    return (0, 12)
                elif totalPts >= 13 and totalPts <= 15:
                    return (13, 15)
                elif totalPts >= 16 and totalPts <= 18:
                    return (16, 18)
                elif totalPts >= 19 and totalPts <= 21:
                    return (19, 21)
                elif totalPts >= 22:
                    return (22, totalPts)
                
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
    Log.write("stubBid: %s in round %d by %s\n" % (bidStr, table.roundNum, table.currentPos.name))
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
    competition = player.teamState.competition
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
                    Log.write("bidUtils: getMyPlayerRole: partner opened\n")
                return PlayerRole.RESPONDER
            else:
                # My partner passed
                Log.write("bidUtils: getMyPlayerRole: partner passed\n")
        else:
            iCanOpen = canIOpen(player.hand, competition, seat) 
            if iCanOpen:
                return PlayerRole.OPENER

    return PlayerRole.UNKNOWN

# FIX ME: dead code?
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


def isShutUpBid(totalPts, bidLevel, bidSuit):
    if bidLevel == 0:
        # Pass
        return True

    if bidSuit.isMinor() and bidLevel == 5:
        return True
    if bidSuit.isMajor() and bidLevel == 4:
        return True
    if bidSuit == Suit.NOTRUMP and bidLevel == 3:
        return True
    
    if totalPts < 33:
        if bidSuit.isMinor() and bidLevel == 5:
            return True
        if bidSuit.isMajor() and bidLevel == 4:
            return True
        if bidSuit == Suit.NOTRUMP and bidLevel == 3:
            return True

    if totalPts < 36 and bidLevel == 6:
        return True

    if bidLevel == 7:
        return True
