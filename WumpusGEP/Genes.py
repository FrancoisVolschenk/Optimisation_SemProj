import random

from Constants import *

class Gene:
    def __init__(self, head_size, num_genes, inheritance = None):
        self.head_space = head_size
        self.num_genes = num_genes
        max_arity = max(list(ARITY.values()))
        self.tail_space = (self.head_space * (max_arity - 1)) + 1
        if inheritance is None:
            self.chromosome = []
            self.init_chromosome()
        else:
            self.chromosome = inheritance

    def init_chromosome(self):
        for g in range(self.num_genes):
            gene = [random.choice(SENSES + ACTIONS) for h in range(self.head_space)]
            gene += [random.choice(ACTIONS) for t in range(self.tail_space)]

            self.chromosome.append(gene)

    def _deepcopy(self, source):
        lstRet = []
        for i in source:
            lstRet.append(i)

        return lstRet

    def express_tree(self, gene):
        actions = self._deepcopy(gene)
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
        for g in range(self.num_genes):
            for h in range(self.head_space):
                if random.random() < mutation_rate:
                    self.chromosome[g][h] = random.choice(SENSES + ACTIONS)

            for t in range(self.tail_space):
                if random.random() < mutation_rate:
                    self.chromosome[g][t] = random.choice(ACTIONS)

if __name__ == "__main__":
    gene = Gene(5, 4)
    print(gene.chromosome)
    for g in range(gene.num_genes):
        print(gene.express_tree(gene.chromosome[g]))
    print('\n' * 2)
    gene.mutate()
    print(gene.chromosome)
    for g in range(gene.num_genes):
        print(gene.express_tree(gene.chromosome[g]))

