import random

# from WumpusWorld import player

SAFE       = 0
DRAFT      = 3
SMELL      = 4
SHIMMER    = 6

ARITY = {SAFE : 2, SMELL: 2, DRAFT: 2, SHIMMER:2, "LEFT": 1, "RIGHT": 1, "FORWARD": 0}

FUNCTIONS = [SAFE, SMELL, DRAFT, SHIMMER]
TERMINALS = ["LEFT", "RIGHT", "FORWARD"]

class Tree:
    def __init__(self, head_space, is_offspring = False):
        self.head_length = head_space
        if not is_offspring:
            self.chromosome = self.init_chromosome()
            self.actions  = [] 
            self.express_tree()
            self.current_node = self.actions
        else:
            self.chromosome = []
            self.actions = []
            self.current_node = None
        self.score = 0
        self.energy = 100

    def get_action(self):
        return self.current_node[0]

    def advance(self, dir = None):
        if len(self.current_node) == 1:
            self.current_node = self.actions
        elif dir is not None:
            if dir == 0:
                self.current_node = self.current_node[1]
            else:
                if len(self.current_node) > 2:
                    self.current_node = self.current_node[2]
    
    def init_chromosome(self):
        # TODO : Find maximum arity dynamically for proper formula
        max_arity = max(list(ARITY.values()))
        self.tail_length = (self.head_length * (max_arity - 1)) + 1
        chromosome = []
        for h in range(self.head_length):
            chromosome.append(random.choice(TERMINALS + FUNCTIONS))
        
        for t in range(self.tail_length):
            chromosome.append(random.choice(TERMINALS))

        return chromosome

    def _deepcopy(self, source):
        lstRet = []
        for i in source:
            lstRet.append(i)

        return lstRet

    def express_tree(self):
        actions = self._deepcopy(self.chromosome)
        actions.reverse()
        self.actions = []
        qSubroots = []
        if len(actions) != 0:
            self.actions.append(actions.pop())
        qSubroots.append(self.actions)
        while len(qSubroots) != 0 and len(actions) != 0:
            subroot = qSubroots[0]
            qSubroots.remove(qSubroots[0])
            arity = ARITY[subroot[0]]
            while arity > 0 and len(actions) != 0:
                subroot.append([actions.pop()])
                arity -= 1
                if ARITY[subroot[-1][0]] != 0:
                    qSubroots.append(subroot[-1])
            
    def mutate(self, mutation_rate = 0.2):
        head_space = self.chromosome[:self.head_length]
        tail_space = self.chromosome[self.head_length:]

        # if random.randint() < 0.5:
        #     head_space[]
        for h in range(len(head_space)):
            if random.random() <= mutation_rate:
                head_space[h] = random.choice(FUNCTIONS + TERMINALS)

        for t in range(len(tail_space)):
            if random.random() <= mutation_rate:
                tail_space[t] = random.choice(TERMINALS)

        self.chromosome = head_space + tail_space
        self.express_tree()
        self.current_node = self.actions



if __name__ == "__main__":
    tree = Tree(6)
    print(tree.chromosome)
    tree.express_tree()
    print(tree.actions)