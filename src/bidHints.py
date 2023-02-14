'''
Functions used to generate bidding hints
'''

from utils import *

def getHintForOpener():
    hintStr = "<6 pts: Pass\n<13 pts\n\t>=6 strong\n\t\tTwo 4+ suit:pass\n\t\t(Len-4)L\nBalanced\n\t15-17: 1NT\n\tStop all suits\n\t\t18-19 hcp: 1L and jump NT\n\t\t20-21 hcp: 2NT\n\t\t25-27 hcp: 3NT\n\t\t28-29 hcp: 4NT\n22+ pts: 2C\nRule of 20:\n\tMajor 5+5: 1S\n\tMajor 4+4: 1H\n\tLong major: 1L\n\tMinor 4+4: 1D\n\tMinor 3+3: 1C\n\tLong minor: 1L"
    return hintStr

def getHintForResponder(level, openSuit):
    if level == 1:
        if openSuit == Suit.CLUB or openSuit == Suit.DIAMOND:
            hintStr = getHintForRespond1Minor()
        elif openSuit == Suit.HEART or openSuit == Suit.SPADE:
            hintStr = getHintForRespond1Major()
        elif openSuit == Suit.NOTRUMP:
            hintStr = getHintForRespond1NT()
    elif level == 2:        
        if openSuit == Suit.CLUB:
            hintStr = getHintForRespond2Club()
        else:
            hintStr = getHintForRespondWeak()
    elif level == 3:
        if openSuit == Suit.NOTRUMP:
            hintStr = getHintForRespond3NT()
        else:
            hintStr = getHintForRespondWeak()        
    return hintStr

def getHintForRespond1Minor():
    hintStr = "Respond to 1 of a minor\n<6 pts: Pass\n4 card major:\n\tMajor 5+5: 1S\n\tMajors 4+4: 1H\n4 card support\n\t6-9 pts: raise\n\t10-11 pts: jump\n\t12+: new suit\n10+ pts\n\tUnbid stoppers\n\t\t16-18 pts: 3NT\n\t\t13-15 pts: 2NT\n\t5+5: higher\n\t4+4: lower\n\tLongest\n4+D over 1C: 1D\n1NT"
    return hintStr

def getHintForRespond1Major():
    hintStr = "Respond to 1 of a major\n<6 pts: Pass\n3+ support\n\t6-9 pts\n\t\t5+ support and single/void: 4B\n\t\t2B\n\t10-11 pts: 2B\n\tNew suit\n4+S over 1H: 1S\n10+ pts\n\t4+ H 2H\n\tUnbid stoppers\n\t\t16-18 pts: 3NT\n\t\t13-15 pts: 2NT\n\t5+5: higher\n\t4+4: lower\n\tLongest\n1NT"
    return hintStr

def getHintForRespond1NT():
    hintStr = "Respond to 1 no trump\n<8 pts\n\t5+ (exc C): 2L\n\tPass\nBalanced and no 4+ major: nNT (2,3,4,6,5,7)\n6+ major and 10-15 pts: 4L\n6+ minor: 3NT\n4 major: 2C\n5+ suit and 10 pts: 3L\n5+ major and 8-9 pts: 2C\nnNT (n=2,3,4,6,5,7)"
    return hintStr

def getHintForRespond2Club:
    hintStr = "Respond to 2 clubs\n<8 pts: 2D\n5+ suit:\n\tD: 3D\n\tL: 2L\nBalanced: 2NT\n2D and rebid"
    return hintStr

def getHintForRespondWeak:
    hintStr = "Respond to weak open\nStoppers in all suits\n\tCan run opener's suit: 3NT\n\tAnother suit with no losers: 3NT\nGame going in long suit: L\nSacrifice and be down <3 tricks: raise\nPass"
    return hintStr

def getHintForRespond3NT:
    hintStr = "Respond to 3NT\n<7 pts: pass\n7 pts: 4NT if not 5+ suit\n8-9 pts: 6NT\n10-11 pts: 5NT\n12+ pts: 7NT"
    return hintStr


def getHintForOpenerRebid(openLevel, openSuit, responderLevel, responderSuit):
    if openLevel == 1:
        if responderLevel == 1:
            if isMinor(openSuit) and isMinor(responderSuit):
                # Responder supported an opening with a minor
                hintStr = getHintForMinorSupport()
            elif isMajor(openSuit) and isMajor(responderSuit):
                # Responder supported an opening with a major
                hintStr = getHintForMajorSupport()
            elif openSuit != responderSuit and responderSuit != Suit.NOTRUMP: 
                # Responder bid new suit at the 1 level
                hintStr = getHintForNewAt1()
            elif responderSuit == Suit.NOTRUMP:
                hintStr = getHintForResponder1NT()
            else:
                print("bidUtils: hintOpenerRebid: ERROR-missing elif")
        elif responderLevel == 2:
            print("bidUtils: hintOpenerRebid: ERROR-No hint yet for responses at the 2 level")
            
    else:
        #hintStr = getOpenerRebidWeak()
        hintStr = "No hint yet for opener rebid of weak opening"
        
    return hintStr


def getHintForResponderRebid():
    hintStr = "Here is the hint for an responder rebid\n"
    return hintStr
