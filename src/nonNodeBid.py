from infoLog import Log
from enums import *
from bidUtils import *
from bidNotif import BidNotif

# This function determines the bid for responding to a Blackwood request
def blackwoodReqHandler(player):
    Log.write("nonNodeBid: processing blackwood req by %s\n" % player.pos.name)
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

    ts.convention = Conv.BLACKWOOD_RSP
    ts.force = Force.ONE_ROUND
    bidNotif = BidNotif(bidLevel, bidSuit, ts)
    ts.convention = Conv.NATURAL
    ts.force = Force.NONE
    return bidNotif

# This function determines the bid for responding to a Gerber request
def gerberReqHandler(player):
    Log.write("nonNodeBid: processing Gerber req by %s\n" % player.pos.name)
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

    ts.convention = Conv.GERBER_RSP
    ts.force = Force.ONE_ROUND
    bidNotif = BidNotif(bidLevel, bidSuit, ts)
    ts.convention = Conv.NATURAL
    ts.force = Force.NONE
    return bidNotif


def nonNodeBidHandler(table, player):
    Log.write("nonNodeBid by %s\n" % player.pos.name)
    ts = player.teamState
    
    # Does the team state show an active convention?
    if ts.convention == Conv.BLACKWOOD_REQ:
        bidNotif = blackwoodReqHandler(player)
        return bidNotif
    elif ts.convention == Conv.GERBER_REQ:
        bidNotif = gerberReqHandler(player)
        return bidNotif
    elif player.teamState.convention != Conv.NATURAL:
        print("nonNodeBidHandler: ERROR - convention %s not handled" % ts.convRsp.name)

    # Did I receive a shut up bid from partner and now should pass?
    if player.teamState.force == Force.PASS:
        ts.convention = Conv.NATURAL
        ts.force = Force.NONE
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

    # Check if team has reached the target game state
    if ts.fitSuit != Suit.ALL:    
        # Get the recommended bid levels for the team's point range
        (minLevel, minGameState) = getBidLevelAndState(ts.teamMinPoints, ts.fitSuit)
        (maxLevel, maxGameState) = getBidLevelAndState(ts.teamMaxPoints, ts.fitSuit)

        print("capt cur: Min level=%d state=%s" % (minLevel, minGameState.name))
        print("capt cur: Max level=%d state=%s" % (maxLevel, maxGameState.name))

        lastTeamBid = findLargestTeamBid(player)
        bidGameState = getGameStateOfBid(lastTeamBid)
        if bidGameState.value >= maxGameState.value:
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
        if bidGameState.value >= minGameState.value:
            bidNotif = BidNotif(0, Suit.ALL, ts)
            return bidNotif
    
    # Check if we should explore slam
    if maxLevel >= 6 and ts.fitSuit != Suit.ALL:
        if ts.partnerNumAces == 4:
            # Explore large slam by asking for kings
            if ts.fitSuit == Suit.NOTRUMP:
                Log.write("nonNodeBid: gerber req for Kings by %s\n" % player.pos.name)
                ts.convention = Conv.GERBER_REQ
                ts.force = Force.ONE_ROUND
                bidNotif = BidNotif(5, Suit.CLUB, ts)
            else:
                Log.write("nonNodeBid: blackwood req for Kings by %s\n" % player.pos.name)
                ts.convention = Conv.BLACKWOOD_REQ
                ts.force = Force.ONE_ROUND
                bidNotif = BidNotif(6, Suit.NOTRUMP, ts)
            ts.convention = Conv.NATURAL
            ts.force = Force.NONE
            return bidNotif
        elif ts.partnerNumAces == -1:
            # Ask partner for number of aces
            if ts.fitSuit == Suit.NOTRUMP:
                Log.write("nonNodeBid: gerber req for Aces by %s\n" % player.pos.name)
                ts.convention = Conv.GERBER_REQ
                ts.force = Force.ONE_ROUND
                bidNotif = BidNotif(4, Suit.CLUB, ts)
            else:
                Log.write("nonNodeBid: blackwood req for Aces by %s\n" % player.pos.name)
                ts.convention = Conv.BLACKWOOD_REQ
                ts.force = Force.ONE_ROUND
                bidNotif = BidNotif(4, Suit.NOTRUMP, ts)
            ts.convention = Conv.NATURAL
            ts.force = Force.NONE
            return bidNotif
    
    # If we get here, the bid is natural. Get a proposed bid
    proposedBid = getProposedBid(table, ts, player)
    proposedBidLevel = proposedBid[0]
    proposedBidSuit = proposedBid[1]
    bidStr = getBidStr(proposedBidLevel, proposedBidSuit)
    print("capt: proposes bid %s" % bidStr)
    
    # Get the recommended bid levels for the team's point range
    (minLevel, minGameState) = getBidLevelAndState(ts.teamMinPoints, proposedBidSuit)
    (maxLevel, maxGameState) = getBidLevelAndState(ts.teamMaxPoints, proposedBidSuit)

    print("capt proposed: Min level=%d state=%s" % (minLevel, minGameState.name))
    print("capt proposed: Max level=%d state=%s" % (maxLevel, maxGameState.name))

    bidGameState = getGameStateOfBid(proposedBid)
    if bidGameState.value < minGameState.value:
        # We want partner to bid again
        # If we have a fit, suggest a new suit
        if ts.fitSuit != Suit.ALL:
            alternateBid = getAlternateBid(table, ts)
            if alternateBid[1] != Suit.ALL:
                # Replace the proposed bid with the alternate
                proposedBidLevel = alternateBid[0]
                proposedBidSuit = alternateBid[1]
        force = Force.ONE_ROUND
    elif bidGameState.value >= maxGameState.value:
        force = Force.PASS
    elif bidGameState.value == minGameState.value and maxGameState.value > minGameState.value:
        force = Force.NONE
    print("capt: force=%s" % (force.name))

    # Now determine where the proposedBidLevel lies wrt the min and maxLevel
    # With a strong hand, we will want to jump a level
    if proposedBidLevel < minLevel:
        if ts.gameState == GameState.GAME:
            actualBidLevel = minLevel
        else:
            actualBidLevel = proposedBidLevel
    elif proposedBidLevel >= minLevel and proposedBidLevel <= maxLevel:
        actualBidLevel = proposedBidLevel
    elif proposedBidLevel > maxLevel:
        actualBidLevel = 0

    print("capt: proposed level=%d actual level=%d force=%s" % (proposedBidLevel, actualBidLevel, force.name))
    
    # Build the notification for a natural bid
    ts.convention = Conv.NATURAL
    ts.force = force
    ts.suitState[proposedBidSuit] = FitState.CANDIDATE
    bidNotif = BidNotif(actualBidLevel, proposedBidSuit, ts)
    return bidNotif


def describerBidHandler(table, player):
    Log.write("describerBidHandler by %s\n" % player.pos.name)
    ts = player.teamState

    # Check the game state of the team
    if ts.gameState == GameState.UNKNOWN:
        # This team likely has passed in the first round
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif

    if ts.force == Force.ONE_ROUND:
        # If we don't have a fit yet, get a proposed bid
        if ts.fitSuit == Suit.ALL:
            proposedBid = getProposedBid(table, ts, player)
        else:
            # Show an alternate suit
            proposedBid = getAlternateBid(table, ts)
        bidNotif = BidNotif(proposedBid[0], proposedBid[1], ts)
        return bidNotif
    
    # Have we reached the target game state?
    lastTeamBid = findLargestTeamBid(player)
    bidGameState = getGameStateOfBid(lastTeamBid)
    if bidGameState.value >= ts.gameState.value:
        # We are done. Just pass.
        bidNotif = BidNotif(0, Suit.ALL, ts)
        return bidNotif

    # If we get here, we have not reached the target game state.
    # We need to continue to describe our hand.
    if table.roundNum < 3:
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
    else:
        # After round 2, we want to show alternate suits
        proposedBid = getAlternateBid(table, ts)
        
    bidNotif = BidNotif(proposedBid[0], proposedBid[1], ts)
    return bidNotif    


# This function proposes a bid. It uses the fit suit if it exists.
# If there is no fit yet, it finds another suit.
# It always bids the selected suit at the lowest level
def getProposedBid(table, ts, player):
    # Do we have a fit?
    if ts.fitSuit == Suit.ALL:
        # We don't have a fit
        # Do I have extra length in the opening suit?
        openingBid = getOpeningBid(ts.bidSeq)
        openingSuit = openingBid[1]
        numCardsOpeningSuit = player.hand.getNumCardsInSuit(openingSuit)
        if numCardsOpeningSuit >= 6 and table.roundNum == 2:
            # We can rebid the opening suit
            proposedBidSuit = openingSuit
        else:            
            # Find a suit that still has a chance of a fit
            if ts.suitState[Suit.HEART] == FitState.UNKNOWN and player.hand.getNumCardsInSuit(Suit.HEART) >= 4:
                proposedBidSuit = Suit.HEART
            elif ts.suitState[Suit.SPADE] == FitState.UNKNOWN and player.hand.getNumCardsInSuit(Suit.SPADE) >= 4:
                proposedBidSuit = Suit.SPADE
            elif ts.suitState[Suit.CLUB] == FitState.UNKNOWN and player.hand.getNumCardsInSuit(Suit.CLUB) >= 4:
                proposedBidSuit = Suit.CLUB
            elif ts.suitState[Suit.DIAMOND] == FitState.UNKNOWN and player.hand.getNumCardsInSuit(Suit.DIAMOND) >= 4:
                proposedBidSuit = Suit.DIAMOND
            else:
                proposedBidSuit = Suit.NOTRUMP
    else:
        # If we get here, we have a known fit
        proposedBidSuit = ts.fitSuit
        
    # What is lowest level I can bid the proposed suit?
    proposedBidLevel = getNextLowestBid(table, proposedBidSuit)

    bidStr = getBidStr(proposedBidLevel, proposedBidSuit)
    print("desc: proposed bid is %s" % bidStr)
    return (proposedBidLevel, proposedBidSuit)

# This function is used to generate a suit which has not previously been bid
def getAlternateBid(table, teamState):
    alternateBidSuit = Suit.ALL
    alternateBidLevel = 0
    for suitValue in range (5, 1, -1):
        suit = Suit(suitValue)
        suitHasBeenBid = False
        # Check if this suit has been bid before
        for bid in teamState.bidSeq:
            if bid[1] == suit:
                suitHasBeenBid = True
                break
        if suitHasBeenBid == False:
            # Found an unbid suit
            alternateBidSuit = suit
            # What is lowest level I can bid the alternate suit?
            alternateBidLevel = getNextLowestBid(table, alternateBidSuit)
            bidStr = getBidStr(alternateBidLevel, alternateBidSuit)
            print("getAlternateBid: returned %s" % bidStr)
            return (alternateBidLevel, alternateBidSuit)
        
    bidStr = getBidStr(alternateBidLevel, alternateBidSuit)
    print("desc: alternate bid is %s" % bidStr)
    return (alternateBidLevel, alternateBidSuit)
