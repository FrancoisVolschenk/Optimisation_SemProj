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
WALL       = 11
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

def distance(p1, p2):
    return math.sqrt(math.pow((p1[0] - p2[0]), 2) + math.pow((p1[1] - p2[1]), 2))

class player:
    def __init__(self, rows, cols, x, y):
        self.rows = rows
        self.cols = cols
        self.direction = 0
        self.x    = x
        self.y    = y
        self.brain = None

    def move(self, move, senses):
        if move in ["LEFT", "RIGHT", "FORWARD"]:
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

            return 1
        elif move == "REMEMBER":
            if (self.x, self.y) in self.brain.memory:
                return 1
            else:
                return 0
        else:
            if move in senses:
                if move != SAFE:
                    self.brain.commit_memory((self.x, self.y))
                return 1
            else:
                return 2


class World:
    def __init__(self, rows, cols, pits, sight_rad, head_space, pop_size, num_gens, mutation_rate = 0.2, crossover_rate = 0.2):
        print("Starting world")
        self.pop_size = pop_size
        self.num_gens = num_gens
        self.head_space = head_space
        self.mutation_rate = mutation_rate
        self.crossover_rate = crossover_rate
        pygame.init()
        self.FONT = pygame.font.SysFont("Arial", TOKEN_SIZE, bold = True)
        self.world_width = cols * TOKEN_SIZE
        self.world_height = rows * TOKEN_SIZE
        self.rows = rows
        self.cols = cols
        self.pits = pits
        
        print("Creating map")
        self.map = [[pygame.rect.Rect((c * TOKEN_SIZE, r * TOKEN_SIZE, TOKEN_SIZE, TOKEN_SIZE)) for c in range(cols)] for r in range(rows)]        
        self.clock = pygame.time.Clock()
        self.reward_map = []
        self.sight_rad = sight_rad
        self.screen = None
        self.player = player(rows, cols, 0, 0)
        print("Initializing population")
        self.brains = [Tree(self.head_space) for _ in range(pop_size)]

    def create_map(self):
        map_types = [[[WALL] if (r == 0) or (c == 0) or (r == self.rows - 1) or (c == self.cols - 1) else [SAFE] for c in range(self.cols)] for r in range(self.rows)]
        self.wump_y = random.randint(1, self.rows - 2)
        self.wump_x = random.randint(1, self.cols - 2)
        
        # print("Placing entities")
        for p in range(self.pits):
            y = random.randint(1, self.rows - 2)
            x = random.randint(1, self.cols - 2)
            while map_types[y][x][0] != SAFE:
                y = random.randint(1, self.rows - 2)
                x = random.randint(1, self.cols - 2)
            for r in range(y - 1, y + 2):
                if r >= 0 and r < self.rows:
                    for c in range(x - 1, x + 2):
                        if c >= 0 and c < self.cols:
                                if r == y or c == x:
                                    map_types[r][c][0] = DRAFT
            map_types[y][x].append(PIT)

        for r in range(self.wump_y - 1, self.wump_y + 2):
            if r >= 0 and r < self.rows:
                for c in range(self.wump_x - 1, self.wump_x + 2):
                    if c >= 0 and  c < self.cols:
                        if r == self.wump_y or c == self.wump_x:
                            if map_types[r][c][0] == SAFE:
                                map_types[r][c][0] = SMELL
                            else:
                                map_types[r][c].insert(0, SMELL)
        map_types[self.wump_y][self.wump_x].append(WUMPUS)

        self.gold_x = random.randint(1, self.cols - 2)
        self.gold_y = random.randint(1, self.rows - 2)
        while map_types[self.gold_y][self.gold_x][0] != SAFE:
            self.gold_x = random.randint(1, self.cols - 2)
            self.gold_y = random.randint(1, self.rows - 2)
        for r in range(self.gold_y - 1, self.gold_y + 2):
            if r >= 0 and r < self.rows:
                for c in range(self.gold_x - 1, self.gold_x + 2):
                    if c >= 0 and c < self.cols:
                        if r == self.gold_y or c == self.gold_x:
                            if map_types[r][c][0] == SAFE:
                                map_types[r][c][0] = SHIMMER
                            else:
                                map_types[r][c].insert(0, SHIMMER)
        map_types[self.gold_y][self.gold_x].append(GOLD)
        self.reward_map = []
        max_dist = self.rows * self.cols
        for r in range(self.rows):
            self.reward_map.append([])
            for c in range(self.cols):
                self.reward_map[r].append(max_dist - distance((self.gold_x, self.gold_y), (c, r)))

        return map_types

    def _draw_text(self, text, colour, x, y):
        img = self.FONT.render(text, True, colour)
        self.screen.blit(img, (x, y))

    def roulette_wheel_selection(self, total_fitness):

        selection_probabilities = [b.score / total_fitness for b in self.brains]
        
        # Spin the roulette wheel
        spin = random.uniform(0, 1)
        cumulative_probability = 0
        
        for i, probability in enumerate(selection_probabilities):
            cumulative_probability += probability
            if cumulative_probability >= spin :
                return self.brains[i]
        
        # In case of rounding errors, return the first individual
        return self.brains[0]
    
    def crossover(self, total_fitness):
        # print("Starting crossover")
        num_survivors = int(self.pop_size * self.crossover_rate)
        new_gen = [self.brains[i] for i in range(num_survivors)]

        # print("Making offspring")
        while len(new_gen) < self.pop_size:
            p1 = self.roulette_wheel_selection(total_fitness)
            p2 = self.roulette_wheel_selection(total_fitness)
            offspring1 = Tree(self.head_space, is_offspring = True)
            offspring1.head = p1.head
            offspring1.head_length = p1.head_length
            offspring1.tail = p2.tail
            offspring1.tail_length = p2.tail_length
            offspring1.chromosome = offspring1.head + offspring1.tail

            offsping2 = Tree(self.head_space, is_offspring = True)
            offsping2.head = p2.head
            offsping2.head_length = p2.head_length
            offsping2.tail = p1.tail
            offsping2.tail_length = p1.tail_length
            offsping2.chromosome = offsping2.head + offsping2.tail

            offspring1.mutate(self.mutation_rate)
            offsping2.mutate(self.mutation_rate)
            new_gen.append(offspring1)
            new_gen.append(offsping2)

        return new_gen
    
    def clear_seen(self, map_types):
        self.reward_map = []
        max_dist = self.rows * self.cols
                
        for r in range(self.rows):
            self.reward_map.append([])
            for c in range(self.cols):
                self.reward_map[r].append(max_dist - distance((self.gold_x, self.gold_y), (c, r)))
                if SEEN in map_types[r][c]:
                    map_types[r][c].remove(SEEN)

    def play_best(self, brain):
        map_types = self.create_map()
        if self.screen is None:
            self.screen = pygame.display.set_mode((self.world_width, self.world_height))
        
        # map_types = self.create_map() #uncomment to shuffle maps 
        pygame.display.set_caption(f'Visualizing best player')

        x = random.randint(2, self.cols - 2)
        y = random.randint(2, self.rows - 2)
        while map_types[y][x][0] != SAFE:
            x = random.randint(2, self.cols - 2)
            y = random.randint(2, self.rows - 2)
        self.player.x = x
        self.player.y = y
        self.player.direction = random.randint(0, 3)
        self.player.brain = brain
        brain.energy = 100
        brain.score = 0
        brain.memory = set()
        self.clear_seen(map_types)
        tree = brain.express_tree()

        run = True
        while run:
            self.clock.tick(20)
            self.screen.fill((0, 0, 0))
            play_x = self.player.x
            play_y = self.player.y

            for r in range(self.rows):
                for c in range(self.cols):
                    if distance((play_x, play_y), (c, r)) >= self.sight_rad:
                        pygame.draw.rect(self.screen, COLOURS[SHROUD], self.map[r][c])
                    else:
                        pygame.draw.rect(self.screen, COLOURS[map_types[r][c][-1]], self.map[r][c])
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

            # brain.energy -= 1
            lstSenses = map_types[self.player.y][self.player.x]
            action = tree[0]
            adv_dir = self.player.move(action, lstSenses)
            if len(tree) == 1:
                tree = brain.express_tree()
            elif adv_dir == 1:
                tree = tree[1]
            else:
                tree = tree[2]

            lstSenses = map_types[self.player.y][self.player.x]
            if PIT in lstSenses or WUMPUS in lstSenses:                
                self._draw_text("You lose! Game Over", (255, 0, 0), 50, 50)
                run = False
            elif GOLD in lstSenses:
                self._draw_text("YOU WIN!", (0, 255, 0), 50, 50)
                run = False
            elif brain.energy <= 0:
                run = False
            
            pygame.display.update()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False

        pygame.quit()  


    def play(self, visualize = False):
        print("Running training")
        # map_types = self.create_map() # Uncomment this to initialize map once 
        if visualize:
            self.screen = pygame.display.set_mode((self.world_width, self.world_height))
        max_score = 0
        for g in range(self.num_gens):
            # print(f"Generation {g}")
            gen_score = 0
            num_found_gold = 0
            map_types = self.create_map() # Comment to prevent map from changing every generation
            if visualize:
                pygame.display.set_caption(f'Generation {g + 1}')
            for b in self.brains:
                x = random.randint(2, self.cols - 2)
                y = random.randint(2, self.rows - 2)
                while map_types[y][x][0] != SAFE:
                    x = random.randint(2, self.cols - 2)
                    y = random.randint(2, self.rows - 2)
                self.player.x = x
                self.player.y = y
                self.player.brain = b
                self.player.direction = random.randint(0, 3)
                b.energy = 100
                b.score = 0
                b.memory = set()
                self.clear_seen(map_types)
                tree = b.express_tree()

                run = True
                while run:
                    # print(f"Energy: {b.energy}")
                    if visualize:
                        self.clock.tick(60)
                        self.screen.fill((0, 0, 0))
                    play_x = self.player.x
                    play_y = self.player.y
                    
                    if visualize:
                        for r in range(self.rows):
                            for c in range(self.cols):
                                if distance((play_x, play_y), (c, r)) >= self.sight_rad:
                                    pygame.draw.rect(self.screen, COLOURS[SHROUD], self.map[r][c])
                                else:
                                    pygame.draw.rect(self.screen, COLOURS[map_types[r][c][-1]], self.map[r][c])
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

                    current_dist = distance((self.gold_x, self.gold_y), (self.player.x, self.player.y))
                    action = tree[0]
                    b.energy -= 1
                    lstSenses = map_types[self.player.y][self.player.x]
                    adv_dir = self.player.move(action, lstSenses)
                    if len(tree) == 1:
                        tree = b.express_tree()
                    elif adv_dir == 1:
                        tree = tree[1]
                    else:
                        tree = tree[2]

                    new_dis = distance((self.gold_x, self.gold_y), (self.player.x, self.player.y))
                    if action == "FORWARD":
                        if SEEN not in map_types[self.player.y][self.player.x]:
                            map_types[self.player.y][self.player.x].insert(0, SEEN)
                            b.score += 1
                        else:
                            b.score -= 2

                    lstSenses = map_types[self.player.y][self.player.x]
                    # if new_dis < current_dist:
                    #     b.score += 2
                    if PIT in lstSenses or WUMPUS in lstSenses:
                        # Game over man
                        b.score -= 100
                        if visualize:
                            self._draw_text("You lose! Game Over", (255, 0, 0), 50, 50)
                        run = False
                    elif GOLD in lstSenses:
                        # you won
                        b.score += 1000
                        num_found_gold += 1
                        if visualize:
                            self._draw_text("YOU WIN!", (0, 255, 0), 50, 50)
                        run = False
                    elif b.energy <= 0:
                        run = False

                    if WALL in lstSenses:
                        b.score -= 2
                    
                    if visualize:
                        self._draw_text(f"Score: {b.score}", (0, 0, 0), 50, 80)
                        pygame.display.update()

                        for event in pygame.event.get():
                            if event.type == pygame.QUIT:
                                run = False
                gen_score += b.score
            # Sort according to score
            self.brains.sort(key = lambda b: b.score, reverse = True) # higher scores first
            print(f"Top score in gen: {g + 1} = {self.brains[0].score} {num_found_gold =}")
            if self.brains[0].score > max_score:
                max_score = self.brains[0].score
                self.brains[0].save()
            self.crossover(gen_score)
        if visualize:
            pygame.quit()   

        smort_brain = None
        with open("top_g.gep", "rb") as fp:
            smort_brain = pickle.load(fp)
        self.play_best(smort_brain)  


if __name__ == "__main__":
    rows = 25
    cols = 20
    head_size = 15
    world = World(rows = rows, cols = cols, pits = 0, sight_rad = 1000, head_space = head_size, 
                  pop_size = 5000, num_gens = 1000, mutation_rate = 0.3)
    world.play(False)
    # smort_brain = None
    # with open("top_g.gep", "rb") as fp:
    #     smort_brain = pickle.load(fp)
    # world.play_best(smort_brain)

