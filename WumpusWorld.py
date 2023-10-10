import pygame
import random
import math
from Tree import *
from time import sleep

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
COLOURS = {SAFE:     (169, 169, 169),
            PIT:     (10, 10, 10), 
            WUMPUS:  (139, 69, 19),
            DRAFT:   (65, 105, 225),
            SMELL:   (95, 158, 160), 
            GOLD:    (255, 223, 0), 
            SHIMMER: (197, 179, 88),
            PLAYER:  (220, 20, 60),
            SHROUD:  (105,105,105),
            INTENT:  (0, 255, 0)}
SENSE = {1: "PIT",
         2: "Wumpus", 
         3: "Draft", 
         4: "Smell", 
         5: "Gold", 
         6: "Shimmer"}
DIRECTIONS = ["up", "right", "down", "left"]

def distance(p1, p2):
    return math.sqrt(math.pow((p1[0] - p2[0]), 2) + math.pow((p1[1] - p2[1]), 2))

class player:
    def __init__(self, rows, cols, x, y):
        self.rows = rows
        self.cols = cols
        self.direction = 0
        self.x    = x
        self.y    = y

    def move(self, move):
        play_x = self.x
        play_y = self.y

        if move == "LEFT":
            # play_x -= 1
            self.direction = (self.direction - 1) % len(DIRECTIONS)
        elif move == "RIGHT":
            # play_x += 1
            self.direction = (self.direction + 1) % len(DIRECTIONS)
        else:
            if self.direction == 0: # if moving up
                # play_y -= 1
                play_y += -1 if move == "FORWARD" else 1
            elif self.direction == 1: # if moving right
                # play_y += 1
                play_x += 1 if move == "FORWARD" else -1
            elif self.direction == 2: # if moving down
                play_y += 1 if move == "FORWARD" else -1
            elif self.direction == 3: # if moving left
                play_x += -1 if move == "FORWARD" else 1

        if (play_x >= 0 and play_x < self.cols) and (play_y >= 0 and play_y < self.rows):
            self.x = play_x
            self.y = play_y


class World:
    def __init__(self, rows, cols, pits, sight_rad, head_space, pop_size, num_gens, mutation_rate = 0.2):
        print("Starting world")
        self.pop_size = pop_size
        self.num_gens = num_gens
        self.head_space = head_space
        self.mutation_rate = mutation_rate
        self.generational_fitness_score = 0
        pygame.init()
        self.FONT = pygame.font.SysFont("Arial", TOKEN_SIZE, bold = True)
        self.world_width = cols * TOKEN_SIZE
        self.world_height = rows * TOKEN_SIZE
        self.rows = rows
        self.cols = cols
        # self.screen = pygame.display.set_mode((self.world_width, self.world_height))
        print("Creating map")
        self.map = [[pygame.rect.Rect((c * TOKEN_SIZE, r * TOKEN_SIZE, TOKEN_SIZE, TOKEN_SIZE)) for c in range(cols)] for r in range(rows)]        
        self.map_types = [[[SAFE] for c in range(cols)] for r in range(rows)]
        self.clock = pygame.time.Clock()
        self.wump_y = random.randint(1, self.rows - 2)
        self.wump_x = random.randint(1, self.cols - 2)
        self.sight_rad = sight_rad
        self.screen = None

        print("Placing entities")
        for p in range(pits):
            y = random.randint(1, self.rows - 2)
            x = random.randint(1, self.cols - 2)
            while self.map_types[y][x][0] != SAFE:
                y = random.randint(1, self.rows - 2)
                x = random.randint(1, self.cols - 2)
            for r in range(y - 1, y + 2):
                if r >= 0 and r < self.rows:
                    for c in range(x - 1, x + 2):
                        if c >= 0 and c < self.cols:
                                if r == y or c == x:
                                    self.map_types[r][c][0] = DRAFT
            self.map_types[y][x].append(PIT)

        for r in range(self.wump_y - 1, self.wump_y + 2):
            if r >= 0 and r < self.rows:
                for c in range(self.wump_x - 1, self.wump_x + 2):
                    if c >= 0 and  c < self.cols:
                        if r == self.wump_y or c == self.wump_x:
                            if self.map_types[r][c][0] == SAFE:
                                self.map_types[r][c][0] = SMELL
                            else:
                                self.map_types[r][c].insert(0, SMELL)
        self.map_types[self.wump_y][self.wump_x].append(WUMPUS)

        self.gold_x = random.randint(1, self.cols - 2)
        self.gold_y = random.randint(1, self.rows - 2)
        while self.map_types[self.gold_y][self.gold_x][0] != SAFE:
            self.gold_x = random.randint(1, self.cols - 2)
            self.gold_y = random.randint(1, self.rows - 2)
        for r in range(self.gold_y - 1, self.gold_y + 2):
            if r >= 0 and r < self.rows:
                for c in range(self.gold_x - 1, self.gold_x + 2):
                    if c >= 0 and c < self.cols:
                        if r == self.gold_y or c == self.gold_x:
                            if self.map_types[r][c][0] == SAFE:
                                self.map_types[r][c][0] = SHIMMER
                            else:
                                self.map_types[r][c].insert(0, SHIMMER)
        self.map_types[self.gold_y][self.gold_x].append(GOLD)
        
        self.player = player(rows, cols, 0, 0)

        print("Initializing population")
        self.brains = [Tree(self.head_space) for _ in range(pop_size)]

    def _draw_text(self, text, colour, x, y):
        img = self.FONT.render(text, True, colour)
        self.screen.blit(img, (x, y))

    def calc_generational_fitness(self):
        self.generational_fitness_score = 0
        for b in self.brains:
            self.generational_fitness_score += math.fabs(b.score)

    def select(self): # roulette wheel selection
        tipover = random.random()
        index = 0
        
        phi = math.fabs(self.brains[index].score) / self.generational_fitness_score
        while phi < tipover:
            # print(f"Roulette turn {index + 1}")
            index = (index + 1) % self.pop_size
            phi += math.fabs(self.brains[index].score) / self.generational_fitness_score
            # print(f"{phi} : {tipover}")

        return self.brains[index]

    def crossover(self):
        self.calc_generational_fitness()
        self.brains.sort(key = lambda p: p.score)
        num_survivors = random.randint(0, self.pop_size // 2) # select a random pool of the elites
        new_gen = []
        # print(f"Saving {num_survivors} individuals from the last generation")
        for s in range(num_survivors):
            new_gen.append(self.brains[s])
            new_gen[-1].score = 0
            new_gen[-1].energy = 100
        # print(f"Filling up the rest of the new generation with new offspring")
        while len(new_gen) != self.pop_size:
            # print("Selecting parent 1")
            p1 = self.select()
            # print("Selecting parent 2")
            p2 = self.select()
            child = Tree(self.head_space, is_offspring = True)
            # print("Crossing over parents")
            # TODO: 1pt or 2pt crossover
            child.chromosome = [p1.chromosome[i] if random.random() < 0.5 else p2.chromosome[i] for i in range(len(p1.chromosome))]
            # print("Mutating child")
            child.mutate(self.mutation_rate)
            new_gen.append(child)

        self.brains = new_gen

    def clear_seen(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if SEEN in self.map_types[r][c]:
                    self.map_types[r][c].remove(SEEN)

    def play(self, pop_size, gens, visualize = False):
        if visualize:
            if self.screen is None:
                self.screen = pygame.display.set_mode((self.world_width, self.world_height))
            # brain = self.brains[0]
            # brain.energy = 100
            # brain.score = 0
        for gen in range(gens):
            for p in range(pop_size):
                self.clear_seen()
                x = self.cols // 2 # random.randint(0, self.cols - 1)
                y = self.rows // 2 # random.randint(0, self.rows - 1)
                # while self.map_types[y][x][0] != SAFE:
                #     x = random.randint(0, self.cols - 1)
                #     y = random.randint(0, self.rows - 1)
                self.player.x = x
                self.player.y = y
                self.player.direction = 0
                self.map_types[y][x].insert(0, SEEN)
                self.brains[p].energy = 100
                self.brains[p].score = 0
                run = True
                while run:
                    play_x = self.player.x
                    play_y = self.player.y
                    current_dist = distance((self.gold_x, self.gold_y), (play_x, play_y))
                    lstSenses = self.map_types[play_y][play_x]
                    if visualize:
                        self.clock.tick(20)
                        self.screen.fill((0, 0, 0))
                        
                        for r in range(self.rows):
                            for c in range(self.cols):
                                if distance((play_x, play_y), (c, r)) >= self.sight_rad:
                                    pygame.draw.rect(self.screen, COLOURS[SHROUD], self.map[r][c])
                                else:
                                    pygame.draw.rect(self.screen, COLOURS[self.map_types[r][c][-1]], self.map[r][c])
                                pygame.draw.rect(self.screen, (0, 0, 0), self.map[r][c], 1)
                        pygame.draw.rect(self.screen, COLOURS[PLAYER], self.map[play_y][play_x])
                        intent_x = play_x
                        intent_y = play_y
                        if self.player.direction == 0: # up
                            intent_y -= 1
                        elif self.player.direction == 1: #right
                            intent_x += 1
                        elif self.player.direction == 2: # down
                            intent_y += 1
                        else: # left
                            intent_x -= 1
                        if (intent_x >= 0 and intent_x < self.cols) and (intent_y >= 0 and intent_y < self.rows):
                            pygame.draw.rect(self.screen, COLOURS[INTENT], self.map[intent_y][intent_x])
                        strSense = SENSE.get(lstSenses[-1], "")
                        self._draw_text(strSense, (255, 255, 255), (self.player.x * TOKEN_SIZE) + TOKEN_SIZE, (self.player.y * TOKEN_SIZE))
                    if self.brains[p].energy <= 0:
                        self.brains[p].score -= 10
                        if visualize:
                            self._draw_text("You ran out of energy", (255, 0, 0), 50, 50)
                        run = False
                    action = self.brains[p].get_action()
                    if action in FUNCTIONS:
                        self.brains[p].energy -= 0.5
                        self.brains[p].score -= 2
                        # lstSenses = self.map_types[self.player.y][self.player.x]
                        # print(f"Looking for {action}")
                        # print(lstSenses)
                        # print(action in lstSenses)
                        if action in lstSenses:
                            # print("left")
                            self.brains[p].advance(0)
                        else:
                            # print("right")
                            self.brains[p].advance(1)
                        # sleep(1)
                    else:
                        self.player.move(action)
                        self.brains[p].energy -= 1
                        if (current_dist > distance((self.gold_x, self.gold_y), (self.player.x, self.player.y))) and (SEEN not in self.map_types[self.player.y][self.player.x]):
                            self.brains[p].score += 10
                            self.map_types[self.player.y][self.player.x].insert(0, SEEN)
                        # if play_x == self.player.x and play_y == self.player.y:
                        #     self.brains[p].score -= 10
                        # elif SEEN not in self.map_types[self.player.y][self.player.x]:
                        #     self.map_types[self.player.y][self.player.x].insert(0, SEEN)
                            # brain.score -= 1
                        else:
                            self.brains[p].score -= 0.5
                        lstSenses = self.map_types[self.player.y][self.player.x]
                        if PIT in lstSenses or WUMPUS in lstSenses:
                            # Game over man
                            self.brains[p].score -= 100
                            if visualize:
                                self._draw_text("You lose! Game Over", (255, 0, 0), 50, 50)
                            run = False
                        elif GOLD in lstSenses:
                            # you won
                            self.brains[p].score += 100
                            print("Found the gold")
                            if visualize:
                                self._draw_text("YOU WIN!", (0, 255, 0), 50, 50)
                            run = False

                    if visualize:
                        pygame.display.update()

                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                run = False
                
                print(f"Generation {gen + 1}, Individual {p + 1}: {self.brains[p].score}")              

            if gen != gens - 1:
                # print(f"Generation {gen + 1}")
                self.crossover()

        print("Done. Visualize Best agent?(y/n)")
        choice = input()
        if choice == "y":
            self.brains.sort(key = lambda p: p.score, reverse = True)
            self.play(1, 1, True)
        else:
            pygame.quit()                   

        # pygame.time.wait(5000)
        # pygame.quit()


if __name__ == "__main__":
    world = World(rows = 30, cols = 50, pits = 25, sight_rad = 10, head_space = 10, pop_size = 1000, num_gens = 100)
    world.play(world.pop_size, world.num_gens)

# TODO: Implement memory in the agent