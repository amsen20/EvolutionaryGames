import numpy as np
import random

from copy import deepcopy

class NeuralNetwork():

    def __init__(self, layer_sizes):

        self.Ws = ['_']
        self.bs = ['_']
        for it in range(1, len(layer_sizes)):
            mat = []
            for i in range(layer_sizes[it]):
                row = []
                for j in range(layer_sizes[it-1]):
                    row.append(random.uniform(-1, 1))
                mat.append(row)
            self.Ws.append(np.array(mat))
            
            self.bs.append(np.zeros((layer_sizes[it], 1)))

    def activation(self, x):
        
        return 1 / (1 + np.exp(-x))

    def forward(self, x):
        
        ll_a = x # last layer a
        for i in range(1, len(self.Ws)):
            ll_a = self.activation((self.Ws[i] @ ll_a) + self.bs[i])
        
        return ll_a
