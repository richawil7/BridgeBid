

from enum import Enum

class Suit(Enum):
    NOTRUMP = 1
    SPADE = 2
    HEART = 3
    DIAMOND = 4
    CLUB = 5
    ALL = 6

class Level(Enum):
    LOW = 0
    Ace_LOW = 1
    Two = 2
    Three = 3
    Four = 4
    Five = 5
    Six = 6
    Seven = 7
    Eight = 8
    Nine = 9
    Ten = 10
    Jack = 11
    Queen = 12
    King = 13
    Ace_HIGH = 14
    HIGH = 15

class TablePosition(Enum):
    NORTH = 0
    EAST = 1
    SOUTH = 2
    WEST = 3
    CONTROL = 4
    CENTER = 5

class DistMethod(Enum):
    HCP_ONLY = 0
    HCP_LONG = 1
    HCP_SHORT = 2

class TeamRole(Enum):
    UNKNOWN = 0,
    OFFENSE = 1,
    DEFENSE = 2
   
class PlayerRole(Enum):
    UNKNOWN = 0,
    OPENER = 1,
    RESPONDER = 2
    NONE = 3
    
class SuitCategory(Enum):
    xxx = 0
    xxQ = 1
    xKx = 2
    Axx = 3
    xKQ = 4
    AxQ = 5
    AKx = 6
    AKQ = 7

class FitState(Enum):
    UNKNOWN = 0
    CANDIDATE = 1
    NO_SUPPORT = 2
    SUPPORT = 3
    
class Force(Enum):
    NONE = 0
    PASS = 1
    ONE_ROUND = 2
    GAME = 3

class Conv(Enum):
    NATURAL = 0
    OPENING = 1
    WEAK_2 = 2
    STAYMAN_REQ = 3
    STAYMAN_RSP = 4
    JACOBY_XFER_REQ = 5
    JACOBY_XFER_RSP = 6
    JACOBY_2NT = 7
    MAJOR_LIMIT = 8
    TWO_OVER_ONE = 9
    SPLINTER = 10
    CUE_BID = 11
    BLACKWOOD_REQ = 12
    BLACKWOOD_RSP = 13
    GERBER_RSP = 14
    GERBER_REQ = 15

class GameState(Enum):
    UNKNOWN = 0
    PARTSCORE = 1
    GAME = 2
    SMALL_SLAM = 3
    LARGE_SLAM = 4
    
# GUI Classes
class PileOrder(Enum):
    FIFO = 1
    LIFO = 2
    
class PileDisplayMode(Enum):
    NONE = 1
    PARTIAL = 2
    FULL = 3
    
