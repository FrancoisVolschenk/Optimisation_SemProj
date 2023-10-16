from Constants import *
import random

ACTIONS = ["UP", "RIGHT", "DOWN", "LEFT", "FORWARD"]

class Policy:
    def __init__(self, start_size, setup = True):
        self.table = dict()
        if setup:
            # for i in range(random.randint(1, start_size)):
            #     sense1 = random.choice(lstStates)
            #     sense2 = random.choice(lstStates)
            #     self.table[(sense1, sense2)] = [random.choice(ACTIONS) for _ in range(random.randint(1, 4))]

            for sense1 in lstStates:
                for sense2 in lstStates:
                    self.table[(sense1, sense2)] = [random.choice(ACTIONS) for _ in range(random.randint(1, 4))]
        self.score = 0
        self.energy = 100
        self.memory = None # store prev seen states

    def mutate(self, mutation_rate = 0.2):
        # print("Before mutation:")
        # print(self.table)
        mutation_type = 1 # random.randint(0, 2)
        # if mutation_type == 0:
        #     print("Grow mutation")
        #     # grow mutation
        #     sense1 = random.choice(lstStates)
        #     sense2 = random.choice(lstStates)
        #     while (sense1, sense2) in self.table.keys():
        #         sense1 = random.choice(lstStates)
        #         sense2 = random.choice(lstStates)
        #     self.table[(sense1, sense2)] = [random.choice(ACTIONS) for _ in range(random.randint(1, 4))]

        if mutation_type == 1:
            # print("Action mutation")
            # action mutation
            for k in self.table.keys():
                for i in range(len(self.table[k])):
                    if random.random() < mutation_rate:
                        self.table[k][i] = random.choice(ACTIONS)

        # print("After mutation")
        # print(self.table)

        # if mutation_type == 2:
        #     # state mutation


if __name__ == "__main__":
    p = Policy(3)
    print(p.table)