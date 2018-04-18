import Box2D
import numpy as np

from evo.car import CarBuilder


class Simulator:
    def __init__(self):
        #self.playground = Playground()
        #self.world = self.playground.world
        self.world = Box2D.b2World()
        self.carBuilder = CarBuilder()
    
    def get_car(self):
        return self.carBuilder.get_random_car()
    
    def get_scores(self, cars):
        for car in cars:
            car.put_to_world(self.world)
        # we need to wait for scores...
        return np.zeros(len(cars))
