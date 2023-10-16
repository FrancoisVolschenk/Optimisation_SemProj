import random
import pickle
from Constants import *
# from WumpusWorld import player

class Tree:
    def __init__(self, head_space, is_offspring = False):
        self.head_length = head_space
        max_arity = max(list(ARITY.values()))
        self.tail_length = (self.head_length * (max_arity - 1)) + 1
        self.head = None
        self.tail = None
        self.init_chromosome()
        self.score = 0
        self.energy = 100
        self.memory = set()

    def advance(self, dir = None):
        if len(self.current_node) == 1:
            self.current_node = self.tree
        elif len(self.current_node) == 2:
            self.current_node = self.current_node[1]
        elif dir is not None:
            if dir == 0:
                self.current_node = self.current_node[1]
            else:
                if len(self.current_node) > 2:
                    self.current_node = self.current_node[2]
    
    def init_chromosome(self):
        self.head = []
        self.tail = []
        for h in range(self.head_length):
            self.head.append(random.choice(TERMINALS + FUNCTIONS))
        
        for t in range(self.tail_length):
            self.tail.append(random.choice(TERMINALS))

        self.chromosome = self.head + self.tail

    def _deepcopy(self, source):
        lstRet = []
        for i in source:
            lstRet.append(i)

        return lstRet

    def express_tree(self):
        actions = self._deepcopy(self.chromosome)
        actions.reverse()
        tree = []
        qSubroots = []
        if len(actions) != 0:
            tree.append(actions.pop())
        qSubroots.append(tree)
        while len(qSubroots) != 0 and len(actions) != 0:
            subroot = qSubroots[0]
            qSubroots.remove(qSubroots[0])
            arity = ARITY[subroot[0]]
            while arity > 0 and len(actions) != 0:
                subroot.append([actions.pop()])
                arity -= 1
                if ARITY[subroot[-1][0]] != 0:
                    qSubroots.append(subroot[-1])

        return tree
            
    def mutate(self, mutation_rate = 0.2):
        for h in range(self.head_length):
            if random.random() <= mutation_rate:
                self.head[h] = random.choice(FUNCTIONS + TERMINALS)

        # if random.random() <= mutation_rate:
        #     self.head_length += 1
        #     self.head.append(random.choice(FUNCTIONS + TERMINALS))

        for t in range(self.tail_length):
            if random.random() <= mutation_rate:
                self.tail[t] = random.choice(TERMINALS)
        
        # max_arity = max(list(ARITY.values()))
        # self.tail_length = (self.head_length * (max_arity - 1)) + 1
        # while(len(self.tail) < self.tail_length):
        #     self.tail.append(random.choice(TERMINALS))

        self.chromosome = self.head + self.tail

    def save(self, file_name = "top_g.gep"):
        with open(file_name, "wb") as fp:
            pickle.dump(self, fp)

    def commit_memory(self, danger):
        self.memory.add(danger)


def Eq(c1, c2):
    if(len(c1) != len(c2)):
        return False
    
    for i in range(len(c1)):
        if(c1[i] != c2[i]):
            print(f"{i = }:{c1[i] = } is not equal to {c2[i] = }")
            return False
        
    return True

if __name__ == "__main__":
    tree = Tree(6)
    c1 = tree._deepcopy(tree.chromosome)
    # print(c1)
    print(tree.chromosome)
    print(tree.express_tree())
    print("==============================================================================")
    trying = 1
    while(Eq(c1, tree.chromosome)):
        tree.mutate()
        print(f"{trying = }")
        trying += 1
    print(tree.chromosome)
    print(tree.express_tree())