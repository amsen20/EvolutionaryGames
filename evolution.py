from copy import deepcopy
from random import randrange
import random
from player import Player
import numpy as np
from config import CONFIG


class Evolution():

    def __init__(self, mode):
        self.mode = mode

    # calculate fitness of players
    def calculate_fitness(self, players, delta_xs):
        for i, p in enumerate(players):
            p.fitness = delta_xs[i]

    def mutate(self, child: Player):

        for b in child.nn.bs:
            if b == '_':
                continue
            b += np.random.normal(0, 0.03, b.shape)

        for W in child.nn.Ws:
            if W == '_':
                continue
            W += np.random.normal(0, 0.03, W.shape)
        
        return child

    def generate_new_population(self, num_players, prev_players=None):

        # in first generation, we create random players
        if prev_players is None:
            return [Player(self.mode) for _ in range(num_players)]

        else:

            # TODO
            # num_players example: 150
            # prev_players: an array of `Player` objects

            # TODO (additional): a selection method other than `fitness proportionate`
            # TODO (additional): implementing crossover

            ps = []
            for player in prev_players:
                ps.append(player.fitness)
            tot = sum(ps)
            ps = [it/tot for it in ps]

            new_players = np.random.choice(prev_players, num_players, p=ps)
            new_players = [self.mutate(deepcopy(it)) if random.random()<0.7 else deepcopy(it) for it in new_players]

            return new_players

    def next_population_selection(self, players, num_players):

        # TODO
        # num_players example: 100
        # players: an array of `Player` objects

        # TODO (additional): a selection method other than `top-k`
        # TODO (additional): plotting

        ps = []
        for player in players:
            ps.append(player.fitness)

        tot = sum(ps)
        ps = [it/tot for it in ps]
        ret = np.random.choice(players, num_players, p=ps, replace=False)
        return list(ret)
