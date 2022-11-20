

from enum import Enum

class Suit(Enum):
    ALL = 0
    SPADE = 1
    HEART = 2
    DIAMOND = 3
    CLUB = 4
    NOTRUMP = 5

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
    LONG = 0
    SHORT = 1

class TeamRole(Enum):
    UNKNOWN = 0,
    OFFENSE = 1,
    DEFENSE = 2
   
class PlayerRole(Enum):
    UNKNOWN = 0,
    OPENER = 1,
    RESPONDER = 2
    
class SuitCategory(Enum):
    xxx = 0
    xxQ = 1
    xKx = 2
    Axx = 3
    xKQ = 4
    AxQ = 5
    AKx = 6
    AKQ = 7
    
# GUI Classes
class PileOrder(Enum):
    FIFO = 1
    LIFO = 2
    
class PileDisplayMode(Enum):
    NONE = 1
    PARTIAL = 2
    FULL = 3
    
