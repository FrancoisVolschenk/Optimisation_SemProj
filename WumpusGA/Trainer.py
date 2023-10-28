"""
Author: F Volschenk - 219030964
This file contains code for estimating the optimum set of moves to solve a given wumpus world map using the genetic algorithm
"""

import math

from numpy import Infinity
from World import World, Player
import random
from Constants import *
from Visualizer import *
import pickle

class Trainer:
    """ This class contains the different components that make up the genetic algorithm"""
    
    def __init__(self, pop_size, mr, cr, patience, initial_sample_size) -> None:
        self.pop_size = pop_size # population size
        self.mr = mr             # mutation rate
        self.cr = cr             # crossover size
        self.patience = patience # when to perform mass extinction
        self.sample_size = initial_sample_size # sample size for use in tournament selection

        self.extinction_count = 0 # Keep track of how many times we did mass extinction
        self.stagnate_count = 0   # Keep track of how many iterations has had no improvements

    def gen_indiv(self, size):
        """ Produce a single, randomly initialized set of moves """
        return [random.choice(ACTIONS) for _ in range(size)]
    
    def tournament_selection(self, population, sample_size, num_select):
        """ Given a population, select a subset of predetermined size, then select the best n individuals (in this case 2) """
        # subset_index = set()
        # while len(subset_index) < sample_size:
        #     subset_index.add(random.randint(0, len(population) - 1))

        # subset = [population[p] for p in subset_index]
        # subset.sort(key = lambda i: i[0], reverse=True)
        # return [subset[n][1] for n in range(num_select)]

        subset = list()
        while len(subset) < sample_size:
            subset.append(random.choice(population))

        subset.sort(key = lambda i: i[0], reverse=True)
        return [subset[n][1] for n in range(num_select)]
        
    def update_values(self, gen_score):
        # if gen score is the same then decreasse sample size
        """ Update the parameters used to control the evolution to try to balance exploration vs exploitation """
        if gen_score[0] > gen_score[1]: # If I have improved since last generation
            self.stagnate_count = 0     # Reset stagnation count
            if self.mr > 0:             # Decrease mutation rate
                self.mr -= 0.001
            # if self.sample_size < self.pop_size:   # increase the selection sample size to increase selective pressure
            #     self.sample_size += 1
        else:                           # If I have worstened or stayed the same
            self.stagnate_count += 1
            if self.mr < 1:             # slightly increase mutation rate. 
                self.mr += 0.001
            # if self.sample_size > 3: # Lowest it can go is 2, since 2 parents need to be selected.
            #     self.sample_size -= 1
    
    def mutate(self, individual):
        """ Applies some genetic mutation to introduce more variety"""
        if random.random() < 0.5: # 50/50 chance to mutate existing genes
            for i in range(len(individual)):
                if random.random() < self.mr:
                    individual[i] = random.choice(ACTIONS)
        else:                     # or to add new genes
            for r in range(random.randint(0, 5)): # add some arbitrary variation in how many genes get added
                if random.random() < self.mr:
                    individual.append(random.choice(ACTIONS))

    def crossover(self, population):
        """ This method produces a new population for the next iteration """

        # Perform Elitism to keep the best n% of the generation alive
        num_survivors = math.floor(self.cr * len(population))
        new_gen = [population[p][1] for p in range(num_survivors)]

        """ The commented out code is an ad hoc Hall of fame selection strategy for selecting parents
            but I typically make use of tournament selection instead """

        # index = 0
        while len(new_gen) < self.pop_size:
            # p1 = population[index][1]
            # index += 1
            # p2 = population[index][1]

            p1, p2 = self.tournament_selection(population, self.sample_size, 2)

            max_p = min(len(p1), len(p2)) # The parents might be of varying lengths, so I must enforce a fair crossover point
            c_point = random.randint(0, max_p)

            # One point crossover to produce two offspring
            off1 = p1[:c_point] + p2[c_point:]
            off2 = p2[:c_point] + p1[c_point:]

            self.mutate(off1)
            self.mutate(off2)

            new_gen.append(off1)
            new_gen.append(off2)        

        return new_gen

    def train(self, rows, cols, num_pits, num_gold, num_wumpi, chromosome_size = 5):
        """ This method applies the GA to find an optimal set of moves to solve a randomly generated world """

        log_file = open("train_log.txt", "w") # logs are kept so that the evolution can be graphed afterwards
        try:
            print("Setting up initial population")
            population = [self.gen_indiv(chromosome_size) for _ in range(self.pop_size)] # Initial population

            print("Generating the training world")
            self.train_world = World(rows, cols, num_pits, num_gold, num_wumpi) # Create the world
            self.train_world.set_map()

            with open("World.bin", "wb") as fp: # Save the world to a file so that the same world can be loaded back in for visualization
                pickle.dump(self.train_world, fp)
            
            px, py = 1, 1 # Start each individual at the same location

            print("Starting Training")
            # Initialise the analysis values
            max_score = -Infinity
            min_moves = Infinity
            best_indiv = None
            num_winners = 0
            generation = -1
            gen_best = [0, 0]

            while num_winners < self.pop_size: # If by some incredible luck, all individuals have solved the world, we can stop
                generation += 1
                score_board = [] # keeps track of each individual's score, and makes rank based sorting easier
                num_winners = 0  # How many in this generation gathered all the gold?
                gen_score = 0    # what was the overall score of the population?
                gen_best[1] = gen_best[0] # Used determine if the best are getting any better
                gen_best[0] = 0

                for individual in population:
                    self.train_world.reset() # Return map to initial state
                    self.train_world.player = Player(rows, cols, px, py) # Create new player with reset score, energy and memory
                    self.train_world.player.energy = len(individual)     # Energy is used to prevent agents from running infinitely

                    action_ptr = -1
                    num_moves = 0
                    run = True

                    while run:
                        action_ptr += 1
                        if self.train_world.player.energy <= 0 or action_ptr >= len(individual):
                            run = False
                            continue

                        # get intended move
                        action = individual[action_ptr]

                        # Move the player
                        self.train_world.player.move(action)
                        num_moves += 1
                        self.train_world.player.energy -= 1

                        # If the player collected gold, increase their score
                        self.train_world.player.score += self.train_world.eval_position()

                        # Determine if the player is in a terminal state
                        state = self.train_world.check_state()
                        if state != ENDSTATES["NOT_DONE"]:
                            run = False
                            if state == ENDSTATES["WON"]: # All gold has been collected
                                self.train_world.player.score += num_gold * 10 # Reward player for each piece of gold they collected
                                num_winners += 1
                                individual = individual[:num_moves + 1] # cut away unused moves

                                if num_moves < min_moves: # If this individual has solved the world in the least amount of moves, they are the current best
                                    min_moves = num_moves
                                    best_indiv = individual

                                    # Preserve this individual in case the training is interrupted
                                    print(f"Saving an individual who solved it in {num_moves}")
                                    with open("Player.txt", "w") as fp:
                                        for move in individual:
                                            fp.write(f"{move}\n")

                            # If the player lost, penalise them based on how they lost
                            if state == ENDSTATES["WUMPUS"]:
                                self.train_world.player.score -= num_wumpi * 10
                                
                            if state == ENDSTATES["PIT"]:
                                self.train_world.player.score -= num_pits * 10

                    self.train_world.player.score -= len(individual) # Penalize for longer chromosome
                    score_board.append((self.train_world.player.score, individual)) # add to score board
                    gen_score += self.train_world.player.score

                    # Keep track of the best score seen so far
                    if self.train_world.player.score > max_score:
                        max_score = self.train_world.player.score
                
                # Sort the population based on their score
                score_board.sort(key = lambda i: i[0], reverse = True)
                gen_best[0] = score_board[0][0] # get the score of the top performer
                gen_score /= self.pop_size

                # Inform the user of progress
                print(f"Top score for gen {generation}: {gen_best[0]} || {num_winners = } {min_moves = }")
                log_file.write(f"{generation}_{gen_score}_{num_winners}_{gen_best[0]}\n") # log generation information for graphing

                # Check if We should carry on as per usual, or do something about stagnation
                if self.stagnate_count >= self.patience:
                    population = [self.gen_indiv(chromosome_size) for _ in range(self.pop_size)] # start fresh with a new population
                    generation = 0
                    self.extinction_count += 1 # keep track of how many times we restarted
                    self.stagnate_count = 0
                    gen_best[0] = 0
                    print("\n\n EXTIONCTION!!! \n\n")
                else:
                    # Create a new population based off of the performance of the current one
                    population = self.crossover(population = score_board)
                    self.update_values(gen_best)
        
        except KeyboardInterrupt: # if the training was stopped by the user, save the progress
            print(f"Best score: {max_score}    min_moves: {min_moves}")
            if best_indiv is not None:
                print("Saving the best individual")
                with open("Player.txt", "w") as fp:
                    for move in best_indiv:
                        fp.write(f"{move}\n")
        log_file.close()

if __name__ == "__main__":
    MUTATION_RATE = 0.8
    ELITE_SIZE = 0.2
    POPULATION_SIZE = 300
    PATIENCE = 150
    SAMPLE_SIZE = 100
    ROWS = 15
    COLS = 25
    PITS = 10

    GOLDS = 5
    WUMPS = 3
    CHROM_SIZE = 20
    trainer = Trainer(POPULATION_SIZE, MUTATION_RATE, ELITE_SIZE, PATIENCE, SAMPLE_SIZE)
    trainer.train(ROWS, COLS, PITS, GOLDS, WUMPS, CHROM_SIZE)
    print("Finished training.")
    print(f"Number of extinctions: {trainer.extinction_count}")
