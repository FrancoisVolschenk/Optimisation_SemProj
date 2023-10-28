import random
import numpy as np

class Layer:
    """This class represents a collection of perceptrons that process a set of inputs and generate a set of outputs"""
    def __init__(self, numInputs: int, numOutputs: int):
        self.numInputs = numInputs
        self.numOutputs = numOutputs
        self.weights = []

        # set up the list of weights for this layer and initialize it with random weights
        for row in range(numInputs):
            self.weights.append([])
            for col in range(numOutputs):
                self.weights[row].append(random.randint(0, 100)/100)

        # set up the biases for this layer
        self.biases = []
        for b in range(numOutputs):
            self.biases.append(random.randint(0, 100)/100)


    # def Activation(self, weightedInput: float) -> int:
    #     """The ReLu function"""
    #     return max(0, weightedInput)

    def Activation(self, weightedInput: float):
        return 1/(1 + np.exp(-weightedInput))
    
    def calcOutputs(self, inputs):
        # This is used for the feedforward function of the network
        activations = []

        # we multiply each of the inputs by the corresponding weight and apply the activation function
        for out in range(self.numOutputs):
            weightedInput = self.biases[out]
            for input in range(self.numInputs):
                weightedInput += inputs[input] * self.weights[input][out]
            activations.append(self.Activation(weightedInput))
        return activations
    
class NeuralNetwork:
    """This class represents the collection of perceptron layers that make up the neural network"""
    def __init__(self, layerSizes):
        self.numLayers = len(layerSizes)
        self.layers = []
        for layer in layerSizes:
            self.layers.append(Layer(layer[0], layer[1]))

    def setBrain(self, brain):
        '''This method accepts a brain as a list of 2-tuples. For each 2-Tuple, [0] == Weights, [1] == Biases'''
        self.layers = [] # Clear the layers that were created by the constructor

        # set the number of layers to the number of bias lists
        numLayers = len(brain)
        self.numLayers = numLayers

        for l in range(numLayers):
            numInputs = len(brain[l][0])
            numOutputs = len(brain[l][1])
            self.layers.append(Layer(numInputs, numOutputs)) # create a new layer
            self.layers[l].weights = brain[l][0] # Set the layer's weights to the corresponding weights from the given brain
            self.layers[l].biases = brain[l][1] # Set the layer's biases to the corresponding bias from the given brain


    def calcOutput(self, inputs):
        # perform the feed forward algorithm for each layer
        for layer in self.layers:
            inputs = layer.calcOutputs(inputs)
        return inputs
    
    def decideAction(self, inputs):
        # given the input, use the network to provide rekevant output
        outputs = self.calcOutput(inputs)
        return outputs.index(max(outputs))
    
    def preserveBrain(self):
        # save the current settings of the weights and biases
        lstBrain = []
        for layer in range(self.numLayers):
            lstBrain.append((self.layers[layer].weights, self.layers[layer].biases))
        return lstBrain

if __name__ == "__main__":
    layer_conf = [[16, 16], [16, 8], [8, 4]]
    test = NeuralNetwork(layer_conf)

    print(test.preserveBrain())