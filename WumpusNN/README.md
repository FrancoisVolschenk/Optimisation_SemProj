# About
This appraoch makes use of a neural network to control the player. The NN will be trained with the genetic algorithm. This means that an initial population is generated with randomly initialized neural networks. Each individual in the population is allowd to play the game and a score is kept on how well that agent performs. The top performing neural networks are then used to reproduce and produce offspring that contain genetic information from two well-performing parents.

# NN Architecture
There are 16 input neurons. Four neurons for each direction (Up, Right, Down, Left). Each group of four neurons contains one to check for SAFE, one to check for SMELL, one to check for DRAFT and one to check for SHIMMER. If the block in that direction is out of bounds, or unexplored, the input neuron recieves a 0, if the block has been explored, the agent can see what is on that block. If the sense in question is present in that block, the neuron receives a 1, else it receives a -1.

There is one hidden layer with 8 neurons. The output layer has 4 neurons, one to represent each direction. The neuron with the highest value is selected as the action to perform. 

The NN makes use of the hyperbolic tangent function as the activation function.