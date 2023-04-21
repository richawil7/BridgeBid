from infoLog import Log
from enums import *
from bidUtils import *
from bidNotif import BidNotif

# This function determines the bid for responding to a Blackwood request
def blackwoodHandler(player):
    Log.write("nonNodeBid: blackwood rsp by %s\n" % player.pos.name)
    ts = player.teamState
    
    # What did my partner bid?
    lastBid = ts.bidSeq[-1]
    if lastBid[0] == 4:
        # Respond with the number of aces we have
        askCardLevel = Level.Ace_HIGH
        bidLevel = 5
    elif lastBid[0] == 5:
        # Respond with the number of kings we have
        askCardLevel = Level.King
        bidLevel = 6
    else:
        bidStr = getBidStr(lastBid[0], lastBid[1])
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

    bidNotif = BidNotif(bidLevel, bidSuit, ts)
    (minPts, maxPts) = getPointRange(player, ts.fitSuit)
    bidNotif.minPoints = minPts
    bidNotif.maxPoints = maxPts
    bidNotif.convention = Conv.BLACKWOOD_RSP
    bidNotif.force = Force.ONE_ROUND
    bidNotif.suitState = ts.suitState
    bidNotif.gameState = ts.gameState
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

    bidNotif = BidNotif(bidLevel, bidSuit, ts)
    (minPts, maxPts) = getPointRange(player, ts.fitSuit)
    bidNotif.minPoints = minPts
    bidNotif.maxPoints = maxPts
    bidNotif.convention = Conv.GERBER_RSP
    bidNotif.force = Force.ONE_ROUND
    bidNotif.suitState = ts.suitState
    bidNotif.gameState = ts.gameState
    return bidNotif


def nonNodeBidHandler(table, player):
    Log.write("nonNodeBid by %s\n" % player.pos.name)
    ts = player.teamState
    
    # Does the team state show an active convention?
    convention = ts.convention
    ts.convention = Conv.NATURAL
    if convention == Conv.BLACKWOOD_REQ:
        bidNotif = blackwoodHandler(player)
        return bidNotif
    elif convention == Conv.GERBER_REQ:
        bidNotif = gerberHandler(player)
        return bidNotif
    elif player.teamState.convention != Conv.NATURAL:
        print("nonNodeBidHandler: ERROR - convention %s not handled" % ts.convRsp.name)

    # Did I receive a shut up bid from partner and now should pass?
    if player.teamState.force == Force.PASS:
        bidNotif = BidNotif(0, Suit.ALL, ts)
        (minPts, maxPts) = getPointRange(player, proposedBidSuit)
        bidNotif.minPoints = minPts
        bidNotif.maxPoints = maxPts
        bidNotif.convention = Conv.NATURAL
        bidNotif.force = Force.NONE
        bidNotif.suitState = ts.suitState
        bidNotif.gameState = ts.gameState
        return bidNotif

    # Am I the Captain of the team?
    if amITheCaptain(player):
        bidNotif = captainBidHandler(table, player)
    else:
        bidNotif = describerBidHandler(table, player)

    # Clear the force variable
    player.teamState.force = Force.NONE
    
    return bidNotif


def captainBidHandler(table, player):
    Log.write("captainBidHandler by %s\n" % player.pos.name)
    ts = player.teamState
    
    # What did the describer bid
    describerBid = ts.bidSeq[-1]
    if describerBid[0] == 0:
        # Describer passed. So we will also pass.
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif
    
    # What is our team's highest bid so far
    teamBid = findLargestTeamBid(player)
    bidStr = getBidStr(teamBid[0], teamBid[1])
    
    bidNotif = None
    # Have we achieved our target game state? If so, we can pass.
    if ts.gameState == GameState.LARGE_SLAM and teamBid[0] == 7:
        bidNotif = BidNotif(0, Suit.ALL, ts)
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
    
    # If we get here, the bid is natural. Get a proposed bid
    proposedBid = getProposedBid(table, ts, player)
    proposedBidLevel = proposedBid[0]
    proposedBidSuit = proposedBid[1]
    
    # Get the recommended bid levels for the team's point range
    (minLevel, minGameState) = getBidLevelAndState(ts.teamMinPoints, proposedBidSuit)
    (maxLevel, maxGameState) = getBidLevelAndState(ts.teamMaxPoints, proposedBidSuit)

    #print("capt: Min level=%d state=%s" % (minLevel, minGameState.name))
    #print("capt: Max level=%d state=%s" % (maxLevel, maxGameState.name))
    
    lastTeamBid = findLargestTeamBid(player)
    bidGameState = getGameStateOfBid(lastTeamBid)
    if bidGameState.value < minGameState.value:
        force = Force.ONE_ROUND
    elif bidGameState.value >= maxGameState.value:
        force = Force.PASS
    elif bidGameState.value == minGameState.value and maxGameState.value > minGameState.value:
        force = Force.NONE
    #print("capt: force=%s" % (force.name))

    # Check if we should explore slam
    if maxLevel >= 6 and ts.fitSuit != Suit.ALL:
        if ts.partnerNumAces == 4:
            # Explore large slam by asking for kings
            if ts.fitSuit == Suit.NOTRUMP:
                Log.write("nonNodeBid: gerber req for Kings by %s\n" % player.pos.name)
                bidNotif = BidNotif(5, Suit.CLUB, ts)
                bidNotif.convention = Conv.GERBER_REQ
            else:
                Log.write("nonNodeBid: blackwood req for Kings by %s\n" % player.pos.name)
                bidNotif = BidNotif(6, Suit.NOTRUMP, ts)
                bidNotif.convention = Conv.BLACKWOOD_REQ
        else:
            # Explore small slam
            if ts.fitSuit == Suit.NOTRUMP:
                Log.write("nonNodeBid: gerber req for Aces by %s\n" % player.pos.name)
                bidNotif = BidNotif(4, Suit.CLUB, ts)
                bidNotif.convention = Conv.GERBER_REQ
            else:
                Log.write("nonNodeBid: blackwood req for Aces by %s\n" % player.pos.name)
                bidNotif = BidNotif(4, Suit.NOTRUMP, ts)
                bidNotif.convention = Conv.BLACKWOOD_REQ

        (minPts, maxPts) = getPointRange(player, ts.fitSuit)
        bidNotif.minPoints = minPts
        bidNotif.maxPoints = maxPts
        bidNotif.force = Force.ONE_ROUND
        bidNotif.suitState = ts.suitState
        bidNotif.gameState = ts.gameState
        return bidNotif
        
    # If we get here, this is a natural bid
    # Now determine where the proposedBidLevel lies wrt the min and maxLevel
    force = Force.NONE
    if proposedBidLevel < minLevel:
        if ts.gameState == GameState.GAME:
            actualBidLevel = minLevel
            force = Force.PASS
        else:
            actualBidLevel = proposedBidLevel
    elif proposedBidLevel >= minLevel and proposedBidLevel <= maxLevel:
        actualBidLevel = proposedBidLevel
    elif proposedBidLevel > maxLevel:
        actualBidLevel = 0
        force = Force.PASS

    print("capt: proposed level=%d actual level=%d force=%s" % (proposedBidLevel, actualBidLevel, force.name))
    
    # Build the notification for a natural bid
    bidNotif = BidNotif(actualBidLevel, proposedBidSuit, ts)
    (minPts, maxPts) = getPointRange(player, proposedBidSuit)
    bidNotif.minPoints = minPts
    bidNotif.maxPoints = maxPts
    bidNotif.convention = Conv.NATURAL
    bidNotif.force = force
    bidNotif.suitState[proposedBidSuit] = FitState.CANDIDATE
    bidNotif.suitState = ts.suitState
    bidNotif.gameState = ts.gameState
    return bidNotif


def describerBidHandler(table, player):
    Log.write("describerBidHandler by %s\n" % player.pos.name)
    ts = player.teamState

    if ts.force == Force.GAME:
        lastTeamBid = findLargestTeamBid(player)
        bidGameState = getGameStateOfBid(lastTeamBid)
        if bidGameState.value < GameState.GAME.value:
            proposedBid = getProposedBid(table, ts, player)
        else:
            proposedBid = (0, Suit.ALL)

    elif ts.force == Force.NONE:
        (hcPts, distPts) = player.hand.evalHand(DistMethod.HCP_SHORT)
        totalPts = hcPts + distPts
        # Compare my actual points against the advertised point range
        rangeSize = ts.myMaxPoints - ts.myMinPoints
        if rangeSize > 5:
            # Split the range into 3 buckets
            numBuckets = 3
        else:
            # Split the range into 2 buckets
            numBuckets = 2
        if totalPts <= ts.myMinPoints + rangeSize/numBuckets:
            proposedBid = (0, Suit.ALL)
        else:
            proposedBid = getProposedBid(table, ts, player)

    elif ts.force == Force.ONE_ROUND:
            proposedBid = getProposedBid(table, ts, player)

    bidNotif = BidNotif(proposedBid[0], proposedBid[1], ts)
    return bidNotif

# This function proposes a bid. It uses the fit suit if it exists.
# If there is no fit yet, it finds another suit.
# It always bids the selected suit at the lowest level
def getProposedBid(table, ts, player):
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
    else:
        # If we get here, we have a known fit
        proposedBidSuit = ts.fitSuit
        
    # What is lowest level I can bid the proposed suit?
    proposedBidLevel = getNextLowestBid(table, proposedBidSuit)

    return (proposedBidLevel, proposedBidSuit)
