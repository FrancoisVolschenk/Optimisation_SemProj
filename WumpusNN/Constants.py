import pygame
pygame.init()


TOKEN_SIZE = 30
SAFE       = 0
PIT        = 1
WUMPUS     = 2
DRAFT      = 3
SMELL      = 4
GOLD       = 5
SHIMMER    = 6
PLAYER     = 7
SHROUD     = 8
SENSES = [SAFE, DRAFT, SMELL, SHIMMER]
SENSES_TRANSLATION = {SAFE: "SAFE", DRAFT: "DRAFT", SMELL: "SMELL", SHIMMER: "SHIMMER", WUMPUS: "WUMPUS", PIT: "PIT", GOLD: "GOLD"}
DANGERS = [DRAFT, SMELL]

cave_img = pygame.image.load("assets/cave.png")
wump_img = pygame.image.load("assets/wumpus.png")
gold_img = pygame.image.load("assets/coin.png")
explorer_img = pygame.image.load("assets/explorer.png")
smell_img = pygame.image.load("assets/Smell.png")
draft_img = pygame.image.load("assets/Draft.png")
shimmer_img = pygame.image.load("assets/Shimmer.png")
pit_img = pygame.image.load("assets/Pit.png")
shroud_img = pygame.image.load("assets/Shroud.png")
cave_img = pygame.transform.scale(cave_img, (TOKEN_SIZE, TOKEN_SIZE))
wump_img = pygame.transform.scale(wump_img, (TOKEN_SIZE, TOKEN_SIZE))
gold_img = pygame.transform.scale(gold_img, (TOKEN_SIZE, TOKEN_SIZE))
explorer_img = pygame.transform.scale(explorer_img, (TOKEN_SIZE, TOKEN_SIZE))
smell_img = pygame.transform.scale(smell_img, (TOKEN_SIZE, TOKEN_SIZE))
draft_img = pygame.transform.scale(draft_img, (TOKEN_SIZE, TOKEN_SIZE))
shimmer_img = pygame.transform.scale(shimmer_img, (TOKEN_SIZE, TOKEN_SIZE))
pit_img = pygame.transform.scale(pit_img, (TOKEN_SIZE, TOKEN_SIZE))
shroud_img = pygame.transform.scale(shroud_img, (TOKEN_SIZE, TOKEN_SIZE))
wump_img.set_colorkey((0, 255, 0))
smell_img.set_colorkey((0, 255, 0))
draft_img.set_colorkey((0, 255, 0))
shimmer_img.set_colorkey((0, 255, 0))

COLOURS = {SAFE:     cave_img,
            PIT:     pit_img, 
            WUMPUS:  wump_img,
            DRAFT:   draft_img,
            SMELL:   smell_img, 
            GOLD:    gold_img, 
            SHIMMER: shimmer_img,
            PLAYER:  explorer_img,
            SHROUD:  shroud_img}
ENDSTATES = {"NOT_DONE": -1, "WON": 0, "WUMPUS": 1, "PIT": 2}
UP = 10
RIGHT = 11
DOWN = 12
LEFT = 13
ACTIONS = ["U", "D", "L", "R"]
ACTIONS_TRANSLATION = {0: "UP", 1: "RIGHT", 2: "DOWN", 3: "LEFT"}
