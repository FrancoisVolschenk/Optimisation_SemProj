import pygame
import random
import math
from Constants import *
from Lookup import *

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

        if move == "UP":
            self.direction = 0
        elif move == "RIGHT":
            self.direction = 1
        elif move == "DOWN":
            self.direction = 2
        elif move == "LEFT":
            self.direction = 3
        elif move == "FORWARD":
            if self.direction == 0: # if moving up
                play_y -= 1
            elif self.direction == 1: # if moving right
                play_x += 1
            elif self.direction == 2: # if moving down
                play_y += 1
            elif self.direction == 3: # if moving left
                play_x -= 1

        if (play_x >= 0 and play_x < self.cols) and (play_y >= 0 and play_y < self.rows):
            self.x = play_x
            self.y = play_y


class World:
    def __init__(self, rows, cols, pits, sight_rad, init_policy_size, pop_size, num_gens, mutation_rate = 0.2, crossover_rate = 0.2):
        print("Starting world")
        self.pop_size = pop_size
        self.num_gens = num_gens
        self.init_policy_size = init_policy_size
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
        self.sight_rad = sight_rad
        self.screen = None
        self.player = player(rows, cols, 0, 0)
        print("Initializing population")
        self.brains = [Policy(self.init_policy_size) for _ in range(pop_size)]

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

        return map_types

    def _draw_text(self, text, colour, x, y):
        img = self.FONT.render(text, True, colour)
        self.screen.blit(img, (x, y))

    def roulette_wheel_selection(self, total_fitness) -> Policy:

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
        if total_fitness == 0:
            total_fitness = 0.01
        num_survivors = int(self.pop_size * self.crossover_rate)
        new_gen = [self.brains[i] for i in range(num_survivors)]

        for n in new_gen:
            n.score = 0
            n.energy = 100
            n.memory = None

        # print("Making offspring")
        while len(new_gen) < self.pop_size:
            p1 = self.roulette_wheel_selection(total_fitness)
            p2 = self.roulette_wheel_selection(total_fitness)
            # print("selected parents")

            keys = p1.table.keys()
            p1_vals = list(p1.table.values())
            p2_vals = list(p2.table.values())

            crossover_point = random.randint(1, len(p1_vals))
            # print("Passing on genes")
            offspring1 = Policy(self.init_policy_size, setup = False)
            offsping2 = Policy(self.init_policy_size, setup = False)
            for i, k in enumerate(keys):
                if i < crossover_point:
                    offspring1.table[k] = p1_vals[i]
                    offsping2.table[k] = p2_vals[i]
                else:
                    offspring1.table[k] = p2_vals[i]
                    offsping2.table[k] = p1_vals[i]
            # print("Mutating offspring")
            offspring1.mutate(self.mutation_rate)
            offsping2.mutate(self.mutation_rate)
            new_gen.append(offspring1)
            new_gen.append(offsping2)
        # print("New generation complete")
        return new_gen
    
    def clear_seen(self, map_types):                
        for r in range(self.rows):
            for c in range(self.cols):
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
        brain.memory = map_types[self.player.y][self.player.x][-1]
        self.clear_seen(map_types)

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
            current_state = lstSenses[-1]
            action = random.choice(brain.table[(brain.memory, current_state)])
            self.player.move(action, lstSenses)
            brain.memory = current_state

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
        # max_score = 0
        for g in range(self.num_gens):
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
                # self.player.brain = b
                self.player.direction = random.randint(0, 3)
                b.energy = 100
                b.score = 0
                # b.memory = None
                self.clear_seen(map_types)
                b.memory = map_types[self.player.y][self.player.x][-1]

                run = True
                while run:
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
                    current_state = map_types[play_y][play_x][-1]
                    action = random.choice(b.table[(b.memory, current_state)])
                    b.energy -= 1
                    self.player.move(action)
                    lstSenses = map_types[self.player.y][self.player.x]
                    b.memory = current_state

                    new_dis = distance((self.gold_x, self.gold_y), (self.player.x, self.player.y))
                    if action == "FORWARD":
                        if SEEN not in map_types[self.player.y][self.player.x]:
                            map_types[self.player.y][self.player.x].insert(0, SEEN)
                            b.score += 1
                        # else:
                        #     b.score -= 2

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
                        b.score -= 1
                    
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
            # if self.brains[0].score > max_score:
            #     max_score = self.brains[0].score
            #     self.brains[0].save()
            self.brains = self.crossover(gen_score)
        if visualize:
            pygame.quit()   

        # smort_brain = None
        # with open("top_g.gep", "rb") as fp:
        #     smort_brain = pickle.load(fp)
        # self.play_best(smort_brain)  


if __name__ == "__main__":
    rows = 25
    cols = 20
    pol_size = 15
    world = World(rows = rows, cols = cols, pits = 10, sight_rad = 1000, init_policy_size= pol_size, 
                  pop_size = 10, num_gens = 10, mutation_rate = 0.3)
    world.play(True)
    # smort_brain = None
    # with open("top_g.gep", "rb") as fp:
    #     smort_brain = pickle.load(fp)
    # world.play_best(smort_brain)

