
from constants import *
from enums import Suit, TablePosition

def writeLog(table, formatStr):
    if table.guiEnabled:
        table.log_fp.write(formatStr)

def getHandStr(hand):
    handStr = ''
    for card in hand.cards:
        cardStr = ''
        if card.level.value == 1 or card.level.value == 14:
            cardStr = 'A'
        elif card.level.value == 13:
            cardStr = 'K'
        elif card.level.value == 12:
            cardStr = 'Q'
        elif card.level.value == 11:
            cardStr = 'J'
        elif card.level.value == 10:
            cardStr = 'T'
        else:
            cardStr = str(card.level.value)
            
        if card.suit == Suit.SPADE:
            cardStr += 'S'
        if card.suit == Suit.HEART:
            cardStr += 'H'
        if card.suit == Suit.DIAMOND:
            cardStr += 'D'
        if card.suit == Suit.CLUB:
            cardStr += 'C'
            
        handStr += cardStr + '-'
    return handStr[:-1]

def getBidStr(bidLevel, bidSuit):
    if bidLevel == 0:
        return "Pass"

    bidStr = "%d" % bidLevel
    if bidSuit == Suit.CLUB:
        bidStr += "C"
    elif bidSuit == Suit.DIAMOND:
        bidStr += "D"
    elif bidSuit == Suit.HEART:
        bidStr += "H"
    elif bidSuit == Suit.SPADE:
        bidStr += "S"
    elif bidSuit == Suit.NOTRUMP:
        bidStr += "N"
    return bidStr

def isMinor(suit):
    return suit == Suit.CLUB or suit == Suit.DIAMOND

def isMajor(suit):
    return suit == Suit.HEART or suit == Suit.SPADE
    
def getNextPosition(currentPosition, leadPosition):
    if TablePosition.NORTH == currentPosition:
        nextPos = TablePosition.EAST
    elif TablePosition.EAST == currentPosition:
        nextPos = TablePosition.SOUTH
    elif TablePosition.SOUTH == currentPosition:
        nextPos = TablePosition.WEST
    elif TablePosition.WEST == currentPosition:
        nextPos = TablePosition.NORTH
    if nextPos == leadPosition:
        return (nextPos, True)
    else:
        return (nextPos, False)

# GUI Functions
def getTableSize():
    return (1200, 600)

def getAnchorPointByPosition(position):
    if position == TablePosition.NORTH or \
       position == TablePosition.SOUTH:
        x_anchor = (400 - (NUM_CARDS_IN_HAND - 1) * CARD_PIXEL_OFFSET - CARD_PIXEL_WIDTH) / 2.0
        y_anchor = (150 - CARD_PIXEL_HEIGHT) / 2.0
        return (x_anchor, y_anchor)
    elif position == TablePosition.EAST or \
         position == TablePosition.WEST:
        x_anchor = (200 - CARD_PIXEL_HEIGHT) / 2.0
        y_anchor = (380 - (NUM_CARDS_IN_HAND - 1) * CARD_PIXEL_OFFSET - CARD_PIXEL_WIDTH) / 2.0
        return (x_anchor, y_anchor)
    elif position == TablePosition.CENTRAL:
        return (0, 0)
    else:
        print("Invalid table position {}".format(position))
            
def isPointInCardField(position, x, y):
    anchor = getAnchorPointByPosition(position)
    # Define the boundries in which card images can live
    x_left = anchor[0]
    x_right = anchor[0] + CARD_PIXEL_OFFSET * NUM_CARDS_IN_HAND + CARD_PIXEL_WIDTH
    y_top = anchor[1]
    y_bottom = anchor[1] + CARD_PIXEL_HEIGHT
    #print("Card field boundries x_left={} x_right={} y_top={} y_bottom={}".format(x_left, x_right, y_top, y_bottom))
    if x >= x_left and x <= x_right and y <= y_bottom and y >= y_top:
        return True
    else:
        return False
