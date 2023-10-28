import random
from Constants import *

class Player:
    def __init__(self, rows, cols, x, y) -> None:
        self.rows = rows
        self.cols = cols
        self.x = x
        self.y = y
        self.seen = set()
        self.energy = 100
        self.score = 0

    def move(self, action, lstSenses):
        tx, ty = self.x, self.y

        if action == 0:
            ty -= 1
        if action == 1:
            tx += 1
        if action == 2:
            ty += 1
        if action == 3:
            tx -= 1

        if (tx >= 0 and tx < self.cols) and (ty >= 0 and ty < self.rows):
            self.x = tx
            self.y = ty
            new_pos = (ty, tx)
            if new_pos not in self.seen:
                self.score += 1
            self.seen.add((ty, tx))

class World:
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
        # Create the grid world
        self.tile_grid = [[[SAFE] for _ in range(self.cols)] for _ in range(self.rows)]

        self._place(self.num_pits, PIT, DRAFT)
        self._place(self.num_gold, GOLD, SHIMMER)
        self._place(self.num_wumpi, WUMPUS, SMELL)

        self.reset()


    def _place(self, num, source, sense = None):
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
        lstToRet = []
        for r in range(len(map)):
            lstToRet.append([])
            for c in range(len(map[r])):
                lstToRet[r].append([])
                for s in range(len(map[r][c])):
                    lstToRet[r][c].append(map[r][c][s])
        return lstToRet

    def reset(self):
        self.cpy_world = []
        self.cpy_world = self._deepcopy(self.tile_grid)
        # for r in range(self.rows):
        #     self.cpy_world.append([])
        #     for c in self.tile_grid[r]:
        #         self.cpy_world[r].append(c)

    def eval_position(self):
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
