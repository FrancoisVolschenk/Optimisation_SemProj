# CONSTANTS
TOKEN_SIZE = 20
SAFE       = 0
PIT        = 1
WUMPUS     = 2
DRAFT      = 3
SMELL      = 4
GOLD       = 5
SHIMMER    = 6
PLAYER     = 7
SHROUD     = 8
SEEN       = 9
INTENT     = 10
WALL       = 11
lstStates = [SAFE, DRAFT, SMELL, SHIMMER, WALL]
COLOURS = {SAFE:     (169, 169, 169),
            PIT:     (10, 10, 10), 
            WUMPUS:  (139, 69, 19),
            DRAFT:   (65, 105, 225),
            SMELL:   (95, 158, 160), 
            GOLD:    (255, 223, 0), 
            SHIMMER: (197, 179, 88),
            PLAYER:  (220, 20, 60),
            SHROUD:  (105,105,105),
            INTENT:  (0, 255, 0),
            WALL:    (50, 20, 20)}
SENSE = {1: "PIT",
         2: "Wumpus", 
         3: "Draft", 
         4: "Smell", 
         5: "Gold", 
         6: "Shimmer"}
DIRECTIONS = ["up", "right", "down", "left"]

ARITY = {SAFE : 2, SMELL: 2, DRAFT: 2, SHIMMER:2, WALL: 2, "LEFT": 1, "RIGHT": 1, "REMEMBER": 2, "FORWARD": 0}

FUNCTIONS = [SAFE, SMELL, DRAFT, SHIMMER, "LEFT", "RIGHT",]# "REMEMBER"] # Last one could be renamed to check memory
TERMINALS = ["FORWARD"]
