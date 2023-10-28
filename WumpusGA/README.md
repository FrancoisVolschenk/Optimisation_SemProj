# About
This appraoch makes use of the genetic algorithm (GA) to evolve the perfect sequence of moves to take in order to solve the world.

# The chromosome
Solutions are represented by a list of varying lengths. The lists contain a sequence of moves (Up, Right, Down, Left). These solutions are allowed to explore the world and are scored based on number of moves taken, number of gold found, and penalised for stepping into a pit or a Wumpus.

During mutation, moves can be randomly changed, or the list can grow with a set of random moves.