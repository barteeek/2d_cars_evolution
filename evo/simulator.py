import Box2D
import numpy as np

from evo.world_entities import CarBuilder
from evo.world_entities import Terrain


class Simulator:
    def __init__(self):
        self.world = Box2D.b2World()
        self.carBuilder = CarBuilder()
        self.terrain = Terrain()
    
    def get_random_individual(self):
        return self.carBuilder.get_random_car()

    def get_scores(self, cars):
        for car in cars:
            car.put_to_world(self.world)

        return np.zeros(len(cars))
