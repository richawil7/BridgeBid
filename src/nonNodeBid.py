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
    bidNotif = BidNotif(player, bidLevel, bidSuit)
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
    bidNotif = BidNotif(player, bidLevel, bidSuit)
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
        print("nonNodeBidHandler: ERROR - convention %s not handled" % ts.convention.name)

    # Did I receive a shut up bid from partner and now should pass?
    if player.teamState.force == Force.PASS:
        ts.convention = Conv.NATURAL
        ts.force = Force.NONE
        bidNotif = BidNotif(player, 0, Suit.ALL)
        return bidNotif

    # What is our team's highest bid so far
    teamBid = findLargestTeamBid(player)
    bidStr = getBidStr(teamBid[0], teamBid[1])
    
    bidNotif = None
    # Have we achieved our target game state? If so, we can pass if not forced to bid
    if ts.force != Force.ONE_ROUND:
        if ts.gameState == GameState.LARGE_SLAM and teamBid[0] == 7:
            bidNotif = BidNotif(player, 0, Suit.ALL)
        elif ts.gameState == GameState.SMALL_SLAM and teamBid[0] == 6:
            bidNotif = BidNotif(player, 0, Suit.ALL)
        elif ts.gameState == GameState.GAME:
            if teamBid[1] == Suit.NOTRUMP and teamBid[0] >= 3:
                bidNotif = BidNotif(player, 0, Suit.ALL)
            elif isMinor(teamBid[1]) and teamBid[0] >= 5:
                bidNotif = BidNotif(player, 0, Suit.ALL)
            elif isMajor(teamBid[1]) and teamBid[0] >= 4:
                bidNotif = BidNotif(player, 0, Suit.ALL)
        elif ts.gameState == GameState.PARTSCORE and teamBid[0] >= 1:
                bidNotif = BidNotif(player, 0, Suit.ALL)
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
        bidNotif = BidNotif(player, 0, Suit.ALL)
        return bidNotif

    # Check if team has reached the target game state
    if ts.fitSuit != Suit.ALL:
        # Get the recommended bid levels for the team's point range
        (minLevel, minGameState) = getBidLevelAndState(ts.teamMinPoints, ts.fitSuit)
        (maxLevel, maxGameState) = getBidLevelAndState(ts.teamMaxPoints, ts.fitSuit)

        Log.write("capt cur: Min level=%d state=%s\n" % (minLevel, minGameState.name))
        Log.write("capt cur: Max level=%d state=%s\n" % (maxLevel, maxGameState.name))

        lastTeamBid = findLargestTeamBid(player)
        bidGameState = getGameStateOfBid(lastTeamBid)
        if bidGameState.value >= maxGameState.value and ts.force == Force.NONE:
            bidNotif = BidNotif(player, 0, Suit.ALL)
            return bidNotif
    
    # Check if we should explore slam
    if ts.fitSuit != Suit.ALL and maxLevel >= 6:
        teamNumAces = ts.partnerNumAces + player.hand.getCountOfCard(Level.Ace_HIGH)
        if teamNumAces == 4:
            # Explore large slam by asking for kings
            if ts.fitSuit == Suit.NOTRUMP:
                Log.write("nonNodeBid: gerber req for Kings by %s\n" % player.pos.name)
                bidNotif = BidNotif(player, 5, Suit.CLUB, Conv.GERBER_REQ, Force.ONE_ROUND)
            else:
                Log.write("nonNodeBid: blackwood req for Kings by %s\n" % player.pos.name)
                bidNotif = BidNotif(player, 6, Suit.NOTRUMP, Conv.BLACKWOOD_REQ, Force.ONE_ROUND)
            return bidNotif
        elif ts.partnerNumAces == -1:
            # Ask partner for number of aces
            if ts.fitSuit == Suit.NOTRUMP:
                Log.write("nonNodeBid: gerber req for Aces by %s\n" % player.pos.name)
                bidNotif = BidNotif(player, 4, Suit.CLUB, Conv.GERBER_REQ, Force.ONE_ROUND)
            else:
                Log.write("nonNodeBid: blackwood req for Aces by %s\n" % player.pos.name)
                bidNotif = BidNotif(player, 4, Suit.NOTRUMP, Conv.BLACKWOOD_REQ, Force.ONE_ROUND)
            return bidNotif
    
    # If we get here, the bid is natural. Get a proposed bid
    proposedBid = getProposedBid(table, ts, player)
    proposedBidLevel = proposedBid[0]
    proposedBidSuit = proposedBid[1]
    bidStr = getBidStr(proposedBidLevel, proposedBidSuit)
    Log.write("capt: proposes bid %s\n" % bidStr)
    
    # Get the recommended bid levels for the team's point range
    (minLevel, minGameState) = getBidLevelAndState(ts.teamMinPoints, proposedBidSuit)
    (maxLevel, maxGameState) = getBidLevelAndState(ts.teamMaxPoints, proposedBidSuit)

    Log.write("capt proposed: Min level=%d state=%s\n" % (minLevel, minGameState.name))
    Log.write("capt proposed: Max level=%d state=%s\n" % (maxLevel, maxGameState.name))

    bidGameState = getGameStateOfBid(proposedBid)
    if bidGameState.value < minGameState.value:
        # How much room do we still have
        if proposedBidLevel + 1 < minLevel:
            # We want partner to bid again
            # If we have a fit, suggest a new suit
            if ts.fitSuit != Suit.ALL:
                alternateBid = getAlternateBid(table, ts)
                if alternateBid[1] != Suit.ALL:
                    # Replace the proposed bid with the alternate
                    proposedBidLevel = alternateBid[0]
                    proposedBidSuit = alternateBid[1]
            force = Force.ONE_ROUND
        elif proposedBidLevel < minLevel and ts.fitSuit == Suit.ALL and proposedBidSuit != ts.candidateSuit:
            force = Force.ONE_ROUND
        else:
            # Just bid the fit suit at the target level
            proposedBidLevel = minLevel
            force = Force.NONE
    elif bidGameState.value >= maxGameState.value:
        force = Force.PASS
    elif bidGameState.value == minGameState.value and maxGameState.value > minGameState.value:
        force = Force.NONE
    Log.write("capt: force=%s\n" % (force.name))

    # Now determine where the proposedBidLevel lies wrt the min and maxLevel
    # With a strong hand, we will want to jump a level if we know our fit suit
    if proposedBidLevel < minLevel:
        if ts.gameState == GameState.GAME:
            if ts.fitSuit == Suit.ALL and ts.candidateSuit != proposedBidSuit:
                actualBidLevel = proposedBidLevel
            else:
                actualBidLevel = minLevel
        else:
            actualBidLevel = proposedBidLevel
    elif proposedBidLevel >= minLevel and proposedBidLevel <= maxLevel:
        actualBidLevel = proposedBidLevel
    elif proposedBidLevel > maxLevel:
        actualBidLevel = 0

    Log.write("capt: proposed level=%d actual level=%d force=%s\n" % (proposedBidLevel, actualBidLevel, force.name))
    
    # Build the notification for a natural bid
    ts.convention = Conv.NATURAL
    ts.force = force
    ts.suitState[proposedBidSuit] = FitState.CANDIDATE
    bidNotif = BidNotif(player, actualBidLevel, proposedBidSuit)
    return bidNotif

def describerBidHandler(table, player):
    Log.write("describerBidHandler by %s\n" % player.pos.name)
    ts = player.teamState
    lastTeamBid = findLargestTeamBid(player)
    bidGameState = getGameStateOfBid(lastTeamBid)

    # Get the target bid level for the fit suit
    targetLevel = getGameStateMinLevel(ts.fitSuit, ts.gameState)
        
    # Check the conditions under which the describer should pass
    if ts.force == Force.PASS:
        bidNotif = BidNotif(player, 0, Suit.ALL)
        return bidNotif
    if ts.force == Force.NONE:
        if ts.fitSuit == lastTeamBid[1]:
            if bidGameState.value >= ts.gameState.value and lastTeamBid[0] >= targetLevel:
                bidNotif = BidNotif(player, 0, Suit.ALL)
                return bidNotif
        
    # Propose a bid
    proposedBid = getProposedBid(table, ts, player)
    if proposedBid[0] == 0 and ts.force != Force.ONE_ROUND:
        bidNotif = BidNotif(player, 0, Suit.ALL)
        return bidNotif
    if proposedBid[0] > targetLevel:
        bidNotif = BidNotif(player, 0, Suit.ALL)
        return bidNotif    
    
    if ts.force == Force.ONE_ROUND and ts.fitSuit != Suit.ALL and lastTeamBid[0] + 1 < targetLevel:
        # We have room to show an alternative bid
        proposedBid = getAlternateBid(table, ts)

    bidNotif = BidNotif(player, proposedBid[0], proposedBid[1])
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
    Log.write("desc: proposed bid is %s\n" % bidStr)
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
            #print("getAlternateBid: returned %s" % bidStr)
            return (alternateBidLevel, alternateBidSuit)
        
    bidStr = getBidStr(alternateBidLevel, alternateBidSuit)
    Log.write("desc: alternate bid is %s" % bidStr)
    return (alternateBidLevel, alternateBidSuit)
