from infoLog import Log
from enums import *
from bidUtils import *
from bidNotif import BidNotif

# This function determines the bid for responding to a Blackwood request
def blackwoodHandler(player):
    Log.write("nonNodeBid: blackwood rsp by %s\n" % player.pos.name)
    ts = player.teamState
    
    # What did my partner bid?
    lastBid = teamState.bidSeq[-1]
    if lastBid[0] == 4:
        # Respond with the number of aces we have
        askCardLevel = Level.Ace_HIGH
        bidLevel = 5
    elif lastBid[0] == 5:
        # Respond with the number of kings we have
        askCardLevel = Level.KING
        bidLevel = 6
    else:
        bidStr = getBidStr(lastBid)
        print("nonNodeBid: blackwood: invalid last bid %s\n" % bidStr)
        return
    
    numCards = player.hand.getCountOfCard(askCardLevel)
    if numCards == 0 or numCards == 4:
        bidSuit = Suit.CLUB
    elif numCards == 1:
        bidSuit = Suit.DIAMOND
    elif numCards == 2:
        bidSuit = Suit.HEART
    elif numCards == 3:
        bidSuit = Suit.SPADE    

    bidNotif = BidNotif(bidLevel, bidSuit)
    (minPts, maxPts) = getPointRange(player, ts.fitSuit)
    bidNotif.setPoints(minPts, maxPts)
    bidNotif.setConv(Conv.BLACKWOOD)
    bidNotif.setForce(Force.ONE_ROUND)
    bidNotif.setSuitState(player.teamState.suitState)
    bidNotif.setGameState(player.teamState.gameState)
    return bidNotif

# This function determines the bid for responding to a Gerber request
def gerberHandler(player):
    Log.write("nonNodeBid: gerber rsp by %s\n" % player.pos.name)
    ts = player.teamState
    
    # What did my partner bid?
    lastBid = teamState.bidSeq[-1]
    if lastBid[0] == 4:
        # Respond with the number of aces we have
        askCardLevel = Level.Ace_HIGH
        bidLevel = 4
    elif lastBid[0] == 5:
        # Respond with the number of kings we have
        askCardLevel = Level.KING
        bidLevel = 5
    else:
        bidStr = getBidStr(lastBid)
        print("nonNodeBid: blackwood: invalid last bid %s\n" % bidStr)
        return
    
    numCards = player.hand.getCountOfCard(askCardLevel)
    if numCards == 0 or numCards == 4:
        bidSuit = Suit.DIAMOND
    elif numCards == 1:
        bidSuit = Suit.HEART
    elif numCards == 2:
        bidSuit = Suit.SPADE
    elif numCards == 3:
        bidSuit = Suit.NOTRUMP    

    bidNotif = BidNotif(bidLevel, bidSuit)
    (minPts, maxPts) = getPointRange(player, ts.fitSuit)
    bidNotif.setPoints(minPts, maxPts)
    bidNotif.setConv(Conv.GERBER)
    bidNotif.setForce(Force.ONE_ROUND)
    bidNotif.setSuitState(player.teamState.suitState)
    bidNotif.setGameState(player.teamState.gameState)
    return bidNotif


def nonNodeBidHandler(table, player):
    Log.write("nonNodeBid by %s\n" % player.pos.name)

    ts = player.teamState
    # Does the team state show an active convention?
    if ts.convention == Conv.BLACKWOOD:
        bidNotif = blackwoodHandler(player)
        return bidNotif
    elif ts.convention == Conv.GERBER:
        bidNotif = gerberHandler(player)
        return bidNotif
    elif player.teamState.convention != Conv.NATURAL:
        print("nonNodeBidHandler: ERROR - convention %s not handled" % ts.convention.name)

    # Did I receive a shut up bid from partner and now should pass?
    if player.teamState.force == Force.PASS:
        bidNotif = BidNotif(0, Suit.ALL)
        (minPts, maxPts) = getPointRange(player, proposedBidSuit)
        bidNotif.setPoints(minPts, maxPts)
        bidNotif.setConv(Conv.NATURAL)
        bidNotif.setForce(Force.NONE)
        bidNotif.setSuitState(player.teamState.suitState)
        bidNotif.setGameState(player.teamState.gameState)
        return bidNotif

    # What is our team's highest bid so far
    teamBid = findLargestTeamBid(player)
    bidStr = getBidStr(teamBid[0], teamBid[1])
    
    bidNotif = None
    # Have we achieved our target game state? If so, we can pass.
    if ts.gameState == GameState.LARGE_SLAM and teamBid[0] == 7:
        bidNotif = BidNotif(0, Suit.ALL)
    elif ts.gameState == GameState.SMALL_SLAM and teamBid[0] == 6:
        bidNotif = BidNotif(0, Suit.ALL, ts)
    elif ts.gameState == GameState.GAME:
        if teamBid[1] == Suit.NOTRUMP and teamBid[0] >= 3:
            bidNotif = BidNotif(0, Suit.ALL, ts)
        elif isMinor(teamBid[1]) and teamBid[0] >= 5:
            bidNotif = BidNotif(0, Suit.ALL, ts)
        elif isMajor(teamBid[1]) and teamBid[0] >= 4:
            bidNotif = BidNotif(0, Suit.ALL, ts)
    elif ts.gameState == GameState.PARTSCORE and teamBid[0] >= 1:
            bidNotif = BidNotif(0, Suit.ALL, ts)
    if bidNotif != None:
        return bidNotif
    
    # If we get here, the bid is natural
    # Do we have a fit?
    if ts.fitSuit == Suit.ALL:
        # We don't have a fit
        # Starting from Clubs and working up, find a suit that still
        # has a chance of a fit
        if ts.suitState[Suit.CLUB] == FitState.UNKNOWN and player.hand.getNumCardsInSuit(Suit.CLUB) >= 4:
            proposedBidSuit = Suit.CLUB
        elif ts.suitState[Suit.DIAMOND] == FitState.UNKNOWN and player.hand.getNumCardsInSuit(Suit.DIAMOND) >= 4:
            proposedBidSuit = Suit.DIAMOND
        elif ts.suitState[Suit.HEART] == FitState.UNKNOWN and player.hand.getNumCardsInSuit(Suit.HEART) >= 4:
            proposedBidSuit = Suit.HEART
        elif ts.suitState[Suit.SPADE] == FitState.UNKNOWN and player.hand.getNumCardsInSuit(Suit.SPADE) >= 4:
            proposedBidSuit = Suit.SPADE
        else:
            proposedBidSuit = Suit.NOTRUMP
            
        # What is lowest level I can bid the proposed suit?
        proposedBidLevel = getNextLowestBid(table, proposedBidSuit)
        
        bidNotif = BidNotif(proposedBidLevel, proposedBidSuit, ts)
        bidNotif.minPoints, bidNotif.maxPoints = getPointRange(player, proposedBidSuit)
        bidNotif.convention = Conv.NATURAL
        bidNotif.force = Force.ONE_ROUND
        bidNotif.suitState[proposedBidSuit] = FitState.CANDIDATE
        return bidNotif
    
    # If we get here, we have a known fit
    # Get the recommended bid levels for the team's point range
    minLevel = getBidLevel(ts.teamMinPoints, ts.fitSuit)
    maxLevel = getBidLevel(ts.teamMaxPoints, ts.fitSuit)
    
    # Compare the teamMaxPoints against the game levels
    if maxLevel >= 6 and ts.fitSuit != Suit.ALL and ts.partnerNumAces == 4:
        # Explore large slam by asking for kings
        if ts.fitSuit == Suit.NOTRUMP:
            Log.write("nonNodeBid: gerber req for Kings by %s\n" % player.pos.name)
            bidNotif = BidNotif(5, Suit.CLUB, ts)
            bidNotif.setConv(Conv.GERBER)
        else:
            Log.write("nonNodeBid: blackwood req for Kings by %s\n" % player.pos.name)
            bidNotif = BidNotif(6, Suit.NOTRUMP, ts)
            bidNotif.setConv(Conv.BLACKWOOD)
    
    if maxLevel >= 6 and ts.fitSuit != Suit.ALL:
        # Explore small slam
        if ts.fitSuit == Suit.NOTRUMP:
            Log.write("nonNodeBid: gerber req for Aces by %s\n" % player.pos.name)
            bidNotif = BidNotif(4, Suit.CLUB, ts)
            bidNotif.setConv(Conv.GERBER)
        else:
            Log.write("nonNodeBid: blackwood req for Aces by %s\n" % player.pos.name)
            bidNotif = BidNotif(4, Suit.NOTRUMP, ts)
            bidNotif.setConv(Conv.BLACKWOOD)
        (minPts, maxPts) = getPointRange(player, ts.fitSuit)
        bidNotif.setPoints(minPts, maxPts)
        bidNotif.setForce(Force.ONE_ROUND)
        bidNotif.setSuitState(player.teamState.suitState)
        bidNotif.setGameState(player.teamState.gameState)
        return bidNotif
        
    # If we get here, this is a natural bid
    # What is lowest level I can bid the fit suit?
    proposedBidLevel = getNextLowestBid(table, ts.fitSuit)
    
    # Now determine where the proposedBidLevel lies wrt the min and maxLevel
    if proposedBidLevel < minLevel:
        actualBidLevel = minLevel
    elif proposedBidLevel >= minLevel and proposedBidLevel <= maxLevel:
        actualBidLevel = proposedBidLevel
    elif proposedBidLevel > maxLevel:
        actualBidLevel = Pass
        
    # Build the notification for a natural bid
    bidNotif = BidNotif(actualBidLevel, ts.fitSuit, ts)
    (minPts, maxPts) = getPointRange(player, ts.fitSuit)
    bidNotif.setPoints(minPts, maxPts)
    bidNotif.setConv(Conv.NATURAL)
    bidNotif.setForce(Force.NONE)
    bidNotif.setSuitState(player.teamState.suitState)
    bidNotif.setGameState(player.teamState.gameState)
    return bidNotif
    
