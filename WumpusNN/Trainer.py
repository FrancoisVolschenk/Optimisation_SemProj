import math

from numpy import Infinity
from World import World, Player
import random
from Constants import *
from Visualizer import *
import pickle
from NN import *

class Trainer:
    def __init__(self, pop_size, num_gens, mr, cr, patience, sample_size, layer_conf) -> None:
        self.pop_size = pop_size
        self.num_gens = num_gens
        self.mr = mr
        self.cr = cr
        self.patience = patience
        self.sample_size = sample_size
        self.layer_conf = layer_conf
    
    def tournament_selection(self, population, sample_size, num_select):
        subset = list()
        while len(subset) < sample_size:
            subset.append(random.choice(population))

        subset.sort(key = lambda i: i[0], reverse=True)
        return [subset[n][1] for n in range(num_select)]
        
    def update_values(self, gen_best):
        if gen_best[0] > gen_best[1]:
            if self.mr > 0:
                self.mr -= 0.001
            if self.sample_size > 1:
                self.sample_size -= 1
        else:
            if self.mr < 1:
                self.mr += 0.001

            if self.sample_size < self.pop_size:
                self.sample_size += 1

    def mutate(self, brain):
        # This method is used to introduce mutations to the weights and biases of the population
        numLayers = len(brain)
        for l in range(numLayers):
            weights = brain[l][0]
            biases = brain[l][1]

            for b in range(len(biases)):
                if random.random ()> self.mr:
                    bias = random.randint(0, 100) / 100
                    biases[b] = bias

            for input in range(len(weights)):
                for output in range(len(weights[input])):
                    if random.random() > self.mr:
                        weights[input][output] += random.randint(0, 100) / 100

    def crossover(self, brain1, brain2):
        # This method is used to mix the genes of the top performers to create agents in the new generation
        parent1 = brain1[1].preserveBrain()
        parent2 = brain2[1].preserveBrain()

        numLayers = len(parent1)
        newBrain = []
        for l in range(numLayers):
            p1Weights = parent1[l][0]
            p1Biases = parent2[l][1]
            p2Weights = parent2[l][0]
            p2Biases = parent2[l][1]

            # there is a 50/50 chance to take a weight gene from either parent
            newWeight = []
            for w in range(len(p1Weights)):
                if random.randint(0, 100) % 2 == 0:
                    newWeight.append(p1Weights[w])
                else:
                    newWeight.append(p2Weights[w])

            # there is a 50/50 chance to take a bias gene from each parent
            newBias = []
            for b in range(len(p1Biases)):
                if random.randint(0, 100) % 2 == 0:
                    newBias.append(p1Biases[b])
                else:
                    newBias.append(p2Biases[b])

            newBrain.append((newWeight, newBias))

        # introduce variety into the population
        self.mutate(newBrain)
        return newBrain

    def createNewGen(self, population):
        # This method uses the existing population to create a new population
        num_survivors = math.floor(self.cr * len(population))
        new_gen = [population[p][1] for p in range(num_survivors)]

        # fill the rest of the remaining population space with new candidates created by breeding the members of the previous population
        popIndex = 0
        while len(new_gen) < self.pop_size:
            newAgent = NeuralNetwork(self.layer_conf)
            newAgent.setBrain(self.crossover(population[popIndex], population[popIndex + 1]))
            popIndex += 1
            new_gen.append(newAgent)
        return new_gen

    def train(self, rows, cols, num_pits, num_gold, num_wumpi):
        log_file = open("train_log.txt", "w")
        try:
            print("Setting up initial population")
            population = [NeuralNetwork(self.layer_conf) for _ in range(self.pop_size)]

            print("Generating the training world")
            self.train_world = World(rows, cols, num_pits, num_gold, num_wumpi)
            self.train_world.set_map()

            # with open("World.bin", "wb") as fp:
            #     pickle.dump(self.train_world, fp)
            px, py = 1, 1

            print("Starting Training")
            max_score = -100
            min_moves = Infinity
            best_indiv = None
            num_winners = 0
            generation = -1
            gen_best = [0, 0]
            while num_winners < self.pop_size:
                # self.train_world.set_map()
                # print(f"{generation = }|| {len(population) = }")
                generation += 1
                score_board = []
                num_winners = 0
                gen_score = 0
                gen_best[1] = gen_best[0]
                gen_best[0] = 0
                for count, individual in enumerate(population):
                    self.train_world.reset()
                    self.train_world.player = Player(rows, cols, px, py)

                    num_moves = 0
                    run = True

                    while run:
                        if self.train_world.player.energy <= 0:
                            run = False
                            continue

                        cx = self.train_world.player.x
                        cy = self.train_world.player.y

                        lstPercepts = []
                        if (cy - 1, cx) in self.train_world.player.seen:
                            up = self.train_world.cpy_world[cy - 1][cx]
                            lstPercepts.append(1 if SAFE in up else -1)
                            lstPercepts.append(1 if DRAFT in up else -1)
                            lstPercepts.append(1 if SMELL in up else -1)
                            lstPercepts.append(1 if SHIMMER in up else -1)
                        else:
                            for _ in range(4):
                                lstPercepts.append(0)
                        if (cy, cx + 1) in self.train_world.player.seen:
                            right = self.train_world.cpy_world[cy][cx + 1]
                            lstPercepts.append(1 if SAFE in right else -1)
                            lstPercepts.append(1 if DRAFT in right else -1)
                            lstPercepts.append(1 if SMELL in right else -1)
                            lstPercepts.append(1 if SHIMMER in right else -1)
                        else:
                            for _ in range(4):
                                lstPercepts.append(0)
                        if (cy + 1, cx) in self.train_world.player.seen:
                            down = self.train_world.cpy_world[cy + 1][cx]
                            lstPercepts.append(1 if SAFE in down else -1)
                            lstPercepts.append(1 if DRAFT in down else -1)
                            lstPercepts.append(1 if SMELL in down else -1)
                            lstPercepts.append(1 if SHIMMER in down else -1)
                        else:
                            for _ in range(4):
                                lstPercepts.append(0)
                        if (cy, cx - 1) in self.train_world.player.seen:
                            left = self.train_world.cpy_world[cy][cx - 1]
                            lstPercepts.append(1 if SAFE in left else -1)
                            lstPercepts.append(1 if DRAFT in left else -1)
                            lstPercepts.append(1 if SMELL in left else -1)
                            lstPercepts.append(1 if SHIMMER in left else -1)
                        else:
                            for _ in range(4):
                                lstPercepts.append(0)

                        
                        action = individual.decideAction(lstPercepts)

                        lstState = self.train_world.cpy_world[cy][cx]
                        self.train_world.player.move(action, lstState)
                        num_moves += 1
                        self.train_world.player.energy -= 1

                        self.train_world.player.score += self.train_world.eval_position()

                        state = self.train_world.check_state()

                        if state != ENDSTATES["NOT_DONE"]:
                            run = False
                            if state == ENDSTATES["WON"]:
                                self.train_world.player.score += num_gold * 10
                                num_winners += 1

                                if num_moves < min_moves:
                                    min_moves = num_moves
                                    max_score = self.train_world.player.score
                                    best_indiv = individual
                                    print(f"Saving an individual who solved it in {num_moves}")
                                    with open("Player.bin", "wb") as fp:
                                        pickle.dump(best_indiv, fp)

                            if state == ENDSTATES["WUMPUS"]:
                                self.train_world.player.score -= num_wumpi * 10
                                
                            if state == ENDSTATES["PIT"]:
                                self.train_world.player.score -= num_pits * 10

                    score_board.append((self.train_world.player.score, individual))
                    gen_score += self.train_world.player.score

                    if self.train_world.player.score > max_score:
                        # best_indiv = individual
                        max_score = self.train_world.player.score
                
                score_board.sort(key = lambda i: i[0], reverse = True)
                gen_best[0] = score_board[0][0]
                print(f"Top score for gen {generation}: {gen_best[0]} || {gen_score = } || {num_winners = } {min_moves = }")
                log_file.write(f"{generation}_{gen_score}_{num_winners}_{gen_best[0]}\n") # log generation information for graphing

                if generation >= self.patience:
                    population = [NeuralNetwork(self.layer_conf) for _ in range(self.pop_size)]
                    generation = 0
                else:
                    population = self.createNewGen(population = score_board)
                    self.update_values(gen_best)
        
        except KeyboardInterrupt:
            print(f"Best score: {max_score}    min_moves: {min_moves}")
            print("Saving the best individual")
            with open("Player.bin", "wb") as fp:
                pickle.dump(best_indiv, fp)
        log_file.close()
        return best_indiv

if __name__ == "__main__":
    MUTATION_RATE = 0.2
    CROSSOVER_RATE = 0.2
    POPULATION_SIZE = 200
    NUM_GENERATIONS = 30
    PATIENCE = 1000
    SAMPLE_SIZE = 100
    ROWS = 10
    COLS = 10
    PITS = 5

    GOLDS = 5
    WUMPS = 5
    LAYER_CONF = [[16, 4]]#, [8, 4]]
    trainer = Trainer(POPULATION_SIZE, NUM_GENERATIONS, MUTATION_RATE, CROSSOVER_RATE, PATIENCE, SAMPLE_SIZE, LAYER_CONF)
    trainer.train(ROWS, COLS, PITS, GOLDS, WUMPS)
