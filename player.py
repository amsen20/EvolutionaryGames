import pygame
import math
import numpy as np

from nn import NeuralNetwork
from copy import deepcopy
from config import CONFIG


class Player():

    def __init__(self, mode, control=False):

        self.control = control  # if True, playing mode is activated. else, AI mode.
        self.pos = [100, 275]   # position of the agent
        self.direction = -1     # if 1, goes upwards. else, goes downwards.
        self.v = 0              # vertical velocity
        self.g = 9.8            # gravity constant
        self.mode = mode        # game mode

        # neural network architecture (AI mode)
        layer_sizes = self.init_network(mode)

        self.nn = NeuralNetwork(layer_sizes)
        self.fitness = 0  # fitness of agent

    def blend(self, other):
        for i in range(1, self.nn.bs):
            self.nn.bs[i] = (self.nn.bs[i] + other.nn.bs[i])/2
        for i in range(1, self.nn.Ws):
            self.nn.Ws[i] = (self.nn.Ws[i] + other.nn.Ws[i])/2

    def move(self, box_lists, camera, events=None):

        if len(box_lists) != 0:
            if box_lists[0].x - camera + 60 < self.pos[0]:
                box_lists.pop(0)

        mode = self.mode

        # manual control
        if self.control:
            self.get_keyboard_input(mode, events)

        # AI control
        else:
            agent_position = [camera + self.pos[0], self.pos[1]]
            self.direction = self.think(mode, box_lists, agent_position, self.v)

        # game physics
        if mode == 'gravity' or mode == 'helicopter':
            self.v -= self.g * self.direction * (1 / 60)
            self.pos[1] += self.v

        elif mode == 'thrust':
            self.v -= 6 * self.direction
            self.pos[1] += self.v * (1 / 40)

        # collision detection
        is_collided = self.collision_detection(mode, box_lists, camera)

        return is_collided

    # reset agent parameters
    def reset_values(self):
        self.pos = [100, 275]
        self.direction = -1
        self.v = 0

    def get_keyboard_input(self, mode, events=None):

        if events is None:
            events = pygame.event.get()

        if mode == 'helicopter':
            self.direction = -1
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.direction = 1

        elif mode == 'thrust':
            self.direction = 0
            keys = pygame.key.get_pressed()
            if keys[pygame.K_UP]:
                self.direction = 1
            elif keys[pygame.K_DOWN]:
                self.direction = -1

        for event in events:
            if event.type == pygame.KEYDOWN:

                if mode == 'gravity' and event.key == pygame.K_SPACE:
                    self.direction *= -1

    def init_network(self, mode):

        # you can change the parameters below

        layer_sizes = None
        if mode == 'gravity':
            layer_sizes = [6, 20, 1]
        elif mode == 'helicopter':
            layer_sizes = [6, 20, 1]
        elif mode == 'thrust':
            layer_sizes = [6, 20, 1]
        return layer_sizes

    
    def think(self, mode, box_lists, agent_position, velocity):

        # TODO
        # mode example: 'helicopter'
        # box_lists: an array of `BoxList` objects
        # agent_position example: [600, 250]
        # velocity example: 7
        cx, cy = agent_position

        mnx = 1e18
        next_box_list = None
        for box_list in box_lists:
            if mnx > box_list.x:
                mnx = box_list.x
                next_box_list = box_list
        
        def dist(x, y):
            return math.sqrt((x-cx)**2 + (y-cy)**2)
        MX = math.sqrt(CONFIG['HEIGHT']**2 + CONFIG['WIDTH']**2)
        data = []
        
        if next_box_list:
            data = [
                cy/CONFIG['HEIGHT'],
                (cy - next_box_list.gap_offset * 60)/CONFIG['HEIGHT'],
                dist(next_box_list.x, next_box_list.gap_mid)/MX,
                (cy - (next_box_list.gap_offset + next_box_list.gap_num) * 60)/CONFIG['HEIGHT'],
                (CONFIG['HEIGHT']-cy)/CONFIG['HEIGHT']
            ]
        

        data.append(velocity/10)
        # print(data)

        out = self.nn.forward(np.reshape(np.array(data), (6, 1)))
        if mode == 'helicopter':
            # print("holo: ", out[0][0])
            direction = 1 if out[0][0] > 0.5 else -1
        if mode == 'gravity':
            direction = 1 if out[0][0] > 0.5 else -1
        if mode == 'thrust':
            if out[0][0] > 2/3:
                direction = 1
            elif out[0][0] > 1/3:
                direction = 0
            else:
                direction = -1
        
        return direction

    def collision_detection(self, mode, box_lists, camera):
        if mode == 'helicopter':
            rect = pygame.Rect(self.pos[0], self.pos[1], 100, 50)
        elif mode == 'gravity':
            rect = pygame.Rect(self.pos[0], self.pos[1], 70, 70)
        elif mode == 'thrust':
            rect = pygame.Rect(self.pos[0], self.pos[1], 110, 70)
        else:
            rect = pygame.Rect(self.pos[0], self.pos[1], 50, 50)
        is_collided = False

        if self.pos[1] < -60 or self.pos[1] > CONFIG['HEIGHT']:
            is_collided = True

        if len(box_lists) != 0:
            box_list = box_lists[0]
            for box in box_list.boxes:
                box_rect = pygame.Rect(box[0] - camera, box[1], 60, 60)
                if box_rect.colliderect(rect):
                    is_collided = True

        return is_collided
