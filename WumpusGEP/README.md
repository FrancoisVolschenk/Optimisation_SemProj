# About
This approach makes use of gene expression programming (GEP) to try and solve the Wumpus world problem.

# GEP Explained
There is a type of evolutionary algorithm known as genetic programming (GP). GP evolves programs or sets of instructions to follow in the form of a tree data-structure. This approach works well when there is native support for trees in a programmng language. Python does not offer native support for trees, so any tree traversal algorithms must be implemented from scratch.

GEP provides an alternative representation of the genes that represent potential solutions. The gene is a simple linear data-structure, like a list, and crossover and mutation can be performed simply by combining slices of these linear data-structures. Once the evolved program needs to be executed, the linear structure can be converted into a tree by performing a level-order traversal.

# The intention
The tree that is built from one of the genes represents a set of instructions that the agent must follow. Each of the internal nodes of the tree represents a decision that should be made based on which sense the player detects on its current square. If the sense is present, execution proceeds along the left branch of the tree, else execution proceeds along the right branch of the tree. Terminal nodes represent actions to be taken. The actions are simply a movement in one of the four directions.

# Future work
I intend to expand the grammar defined for the trees to increase the abilities that the agent can evolve. The hope is that a larger grammar may result in potential solutions being found.

Another aspect to look into is a new fitness function to reward agents for exploring the world and for surviving longer.