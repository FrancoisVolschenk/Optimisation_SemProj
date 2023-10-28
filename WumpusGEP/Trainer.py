import math

from numpy import Infinity
from World import World, Player
import random
from Genes import Gene
from Constants import *
from Visualizer import *
import pickle

class Trainer:
    def __init__(self, pop_size, num_gens, mr, cr, patience, sample_size, head_size, num_genes) -> None:
        self.pop_size = pop_size
        self.num_gens = num_gens
        self.mr = mr
        self.cr = cr
        self.patience = patience
        self.sample_size = sample_size
        self.head_size = head_size
        self.num_genes = num_genes
    
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
            # if self.sample_size > 1:
            #     self.sample_size -= 1
        else:
            if self.mr < 1:
                self.mr += 0.001

            # if self.sample_size < self.pop_size:
            #     self.sample_size += 1

    def crossover(self, population):
        # print("Starting crossover")

        num_survivors = math.floor(self.cr * len(population))
        new_gen = [population[p][1] for p in range(num_survivors)]
        # new_gen = [population[0][1]]

        # index = 0
        while len(new_gen) < self.pop_size:
            # p1 = population[index][1]
            # index += 1
            # p2 = population[index][1]
            p1, p2 = self.tournament_selection(population, self.sample_size, 2)

            c_point = random.randint(0, len(p1.chromosome))

            off1 = p1.chromosome[:c_point] + p2.chromosome[c_point:]
            off2 = p2.chromosome[:c_point] + p1.chromosome[c_point:]

            offspring1 = Gene(self.head_size, self.num_genes, inheritance = off1)
            offspring2 = Gene(self.head_size, self.num_genes, inheritance = off2)

            offspring1.mutate(self.mr)
            offspring2.mutate(self.mr)

            new_gen.append(offspring1)
            new_gen.append(offspring2)        

        return new_gen

    def train(self, rows, cols, num_pits, num_gold, num_wumpi):
        log_file = open("train_log.txt", "w")
        try:
            print("Setting up initial population")
            population = [Gene(self.head_size, self.num_genes) for _ in range(self.pop_size)]

            print("Generating the training world")
            self.train_world = World(rows, cols, num_pits, num_gold, num_wumpi)
            

            # with open("World.bin", "wb") as fp:
            #     pickle.dump(self.train_world, fp)
            

            print("Starting Training")
            max_score = -100
            min_moves = Infinity
            best_indiv = None
            num_winners = 0
            generation = -1
            gen_best = [0, 0]
            while num_winners < self.pop_size:
                self.train_world.set_map()
                px = random.randint(0, cols - 1)
                py = random.randint(0, rows - 1)
                while SAFE not in self.train_world.cpy_world[py][px]:
                    px = random.randint(0, cols - 1)
                    py = random.randint(0, rows - 1)
                generation += 1
                score_board = []
                num_winners = 0
                gen_score = 0
                gen_best[1] = gen_best[0]
                gen_best[0] = 0
                for individual in population:
                    self.train_world.reset()
                    self.train_world.player = Player(rows, cols, px, py)

                    gene_ptr = 0
                    action_ptr = individual.express_tree(individual.chromosome[gene_ptr])
                    num_moves = 0
                    run = True

                    while run:
                        if self.train_world.player.energy <= 0:
                            run = False
                            continue

                        action = action_ptr[0]

                        lstState = self.train_world.cpy_world[self.train_world.player.y][self.train_world.player.x]
                        adv_dir = self.train_world.player.move(action, lstState)
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

                        if adv_dir == 0:
                            gene_ptr = (gene_ptr + 1) % len(individual.chromosome)
                            action_ptr = individual.express_tree(individual.chromosome[gene_ptr])
                        else: # adv_dir is either 1 or 2
                            if adv_dir < len(action_ptr): # some safety checks
                                action_ptr = action_ptr[adv_dir]
                            else:
                                gene_ptr = (gene_ptr + 1) % len(individual.chromosome)
                                action_ptr = individual.express_tree(individual.chromosome[gene_ptr])

                    score_board.append((self.train_world.player.score, individual))
                    gen_score += self.train_world.player.score

                    if self.train_world.player.score > max_score:
                        best_indiv = individual
                        max_score = self.train_world.player.score
                
                score_board.sort(key = lambda i: i[0], reverse = True)
                gen_best[0] = score_board[0][0]
                print(f"Top score for gen {generation}: {gen_best[0]} || {num_winners = } {min_moves = }")
                log_file.write(f"{generation}_{gen_score}_{num_winners}_{gen_best[0]}\n") # log generation information for graphing

                if generation >= self.patience: # mass extinction
                    if random.random() < 0.5:
                        self.head_size += 1
                    else:
                        self.num_genes += 1
                    population = [Gene(self.head_size, self.num_genes) for _ in range(self.pop_size)]
                    generation = 0
                    gen_best[0] = 0
                else:
                    population = self.crossover(population = score_board)
                    self.update_values(gen_best)
        
            # self.train_world.player = Player(rows, cols, px, py)
        except KeyboardInterrupt:
            print(f"Best score: {max_score}    min_moves: {min_moves}")
            print("Saving the best individual")
            with open("Player.bin", "wb") as fp:
                pickle.dump(best_indiv, fp)
            print("Saved best individual")
        log_file.close()
        return best_indiv

if __name__ == "__main__":
    MUTATION_RATE = 0.8
    CROSSOVER_RATE = 0.2
    POPULATION_SIZE = 300
    NUM_GENERATIONS = 30
    PATIENCE = 200
    SAMPLE_SIZE = 100
    HEAD_SIZE = 10
    NUM_GENES = 5
    ROWS = 10
    COLS = 15
    PITS = 15

    GOLDS = 3
    WUMPS = 3
    trainer = Trainer(POPULATION_SIZE, NUM_GENERATIONS, MUTATION_RATE, CROSSOVER_RATE, PATIENCE, SAMPLE_SIZE, HEAD_SIZE, NUM_GENES)
    best = trainer.train(ROWS, COLS, PITS, GOLDS, WUMPS)

