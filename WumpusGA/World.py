"""
Author: F Volschenk - 219030964
This file contains code for maintaining the state of the world and player
"""

import random
from Constants import *

class Player:
    """ This class represents the player that explores the world """
    def __init__(self, rows, cols, x, y) -> None:
        self.rows = rows
        self.cols = cols
        self.x = x
        self.y = y
        self.seen = set()
        self.energy = 100
        self.score = 0

    def move(self, action):
        """ Move in the specified direction """
        tx, ty = self.x, self.y

        if action == "U":
            ty -= 1
        if action == "R":
            tx += 1
        if action == "D":
            ty += 1
        if action == "L":
            tx -= 1

        if (tx >= 0 and tx < self.cols) and (ty >= 0 and ty < self.rows): # Only move if the new position is valid 
            self.x = tx
            self.y = ty
            new_pos = (ty, tx)
            if new_pos not in self.seen: # Remember visited squares 
                self.score += 1
            self.seen.add((ty, tx))

class World:
    """ This class maintains the state of the world """
    def __init__(self, rows, cols, num_pits, num_gold, num_wumpi):
        self.rows = rows
        self.cols = cols
        self.num_pits = num_pits
        self.num_gold = num_gold
        self.num_wumpi = num_wumpi

        self.tile_grid = None
        self.cpy_world = None
        self.player = None


    def set_map(self):
        """ Place the specified number of world entities at random places in the world """
        # Create the grid world
        self.tile_grid = [[[SAFE] for _ in range(self.cols)] for _ in range(self.rows)]

        self._place(self.num_pits, PIT, DRAFT)
        self._place(self.num_gold, GOLD, SHIMMER)
        self._place(self.num_wumpi, WUMPUS, SMELL)

        self.reset()


    def _place(self, num, source, sense = None):
        """ This method removes repetitive code for placing each type of entity and its surrounding senses """
        for _ in range(num):
            px = random.randint(0, self.cols - 1)
            py = random.randint(0, self.rows - 1)
            while self.tile_grid[py][px][-1] not in SENSES:
                px = random.randint(0, self.cols - 1)
                py = random.randint(0, self.rows - 1)
            self.tile_grid[py][px] = [source]
            if sense is not None:
                for r in range(py - 1, py + 2):
                    if r >= 0 and r < self.rows:
                        for c in range(px - 1, px + 2):
                            if c >= 0 and c < self.cols:
                                    if (r == py or c == px) and self.tile_grid[r][c][-1] in SENSES:
                                        self.tile_grid[r][c].append(sense)
                                        if SAFE in self.tile_grid[r][c]:
                                            self.tile_grid[r][c].remove(SAFE)

    def _deepcopy(self, map):
        """ This method makes a deep copy of a map, used to make copies for each agent to explore """
        lstToRet = []
        for r in range(len(map)):
            lstToRet.append([])
            for c in range(len(map[r])):
                lstToRet[r].append([])
                for s in range(len(map[r][c])):
                    lstToRet[r][c].append(map[r][c][s])
        return lstToRet

    def reset(self):
        """ This method is used to clear any progress made to the map by producing a clean copy """
        self.cpy_world = []
        self.cpy_world = self._deepcopy(self.tile_grid)

    def eval_position(self):
        """ This method determines if the player has found gold and if so, removes the gold and its shimmer """
        px, py = self.player.x, self.player.y
        retval = 0
        if GOLD in self.cpy_world[py][px]:
            retval = 50
            self.cpy_world[py][px].remove(GOLD)
            if len(self.cpy_world[py][px]) == 0:
                self.cpy_world[py][px] = [SAFE]
            for r in range(py - 1, py + 2):
                if r >= 0 and r < self.rows:
                    for c in range(px - 1, px + 2):
                        if c >= 0 and c < self.cols:
                            if SHIMMER in self.cpy_world[r][c]:
                                self.cpy_world[r][c].remove(SHIMMER)
                            if len(self.cpy_world[r][c]) == 0:
                                self.cpy_world[r][c] = [SAFE]
        return retval


    def check_state(self):
        """ This method checks if all the gold has been collected, if the player is in a pit or on a wumpus """
        px, py = self.player.x, self.player.y

        if WUMPUS in self.cpy_world[py][px]:
            return ENDSTATES["WUMPUS"]
        if PIT in self.cpy_world[py][px]:
            return ENDSTATES["PIT"]
        
        num_gold = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if GOLD in self.cpy_world[r][c]:
                    num_gold += 1
        if num_gold == 0:
            return ENDSTATES["WON"]
        
        return ENDSTATES["NOT_DONE"]
