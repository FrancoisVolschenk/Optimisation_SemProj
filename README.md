# About
This is a project for a course in optimisation. The course covers techniques such as evolutionary algorithms, particle swarms and ant colonies.

The goal of this project is to make use of evolutionary algorithms, specifically the genetic algorithm, to try and solve the wumpus world problem.

# Wumpus World
The world represents a cave with several rooms. Each of these rooms is shown as a square in a grid. There is gold scattered throughout the world, but there are also many pits to fall into, and some deadly monsters called the Wumpus.

- When the player is in a room adjacent to the gold, it can see a shimmer.
- When te player is in a room adjacent to a pit, it can feel a draft.
- When the player is in a room adjacent to a Wumpus, it can smell the Wumpus.

However, the player does not know which direction the sense is comming from. Therefore, it must use knowledge built up by exploring the world to figure out where the source of the sense is comming from.

# The solutions
I implemented three different approaches to try to solve this problem. In the end only one of the appraoches yielded consistent results. The GA implementation is capable of producing a solution that can solve the world, and given enough time it could generate a solution that solves the world in the least amount of moves possible.

The NN appraoch shows potential, as the population score increased steadily consistently. The GEP approach yielded no consistent improvement over many generations.

# Playing the game
If you wish to play the game yourself, run the Visualizer.py file. The size of the world, number of golds, pits and Wumpuses can be set from the main function.

If you wish to train the AI to solve the problem, run Train.py