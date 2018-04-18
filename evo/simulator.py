import Box2D
import numpy as np

from evo.world_entities import CarBuilder
from evo.world_entities import Terrain


class Simulator:
    def __init__(self, vel_iters, pos_iters, route_len):
        self.world = Box2D.b2World()
        self.carBuilder = CarBuilder()
        self.terrain = Terrain(route_len)
        self.end_of_route = self.terrain.put_to_world(self.world)
        self.vel_iters = vel_iters
        self.pos_iters = pos_iters
        self.speed = 50
    
    def get_random_individual(self):
        return self.carBuilder.get_random_car()

    def wait_until_falls_down(self, car_body):
        init_y = car_body.position[1]
        while True:
            self._run(1)
            new_y = car_body.position[1]
            if np.abs(init_y - new_y) < 10e-3:
                break

            init_y = new_y

    def _run(self, iters):
        for i in range(iters):
            for j in range(60):
                self.world.Step(1. / 60., self.vel_iters, self.pos_iters)
                self.world.ClearForces()

    def run(self, body, springs):
        prev_x = np.inf
        springs[0].motorSpeed = -self.speed
        self._run(100)
        while (not (self.end_of_route[0] <= body.position[0] <= self.end_of_route[1])) and \
            np.abs(prev_x - body.position[0]) >= 10e-4:
            self._run(100)
            prev_x = body.position[0]

        if self.end_of_route[0] <= body.position[0] <= self.end_of_route[1]:
            return self.end_of_route[0]
        return body.position[0]

    def get_scores(self, cars):
        scores = np.zeros(len(cars))
        for i, car in enumerate(cars):
            body, wheels, springs = car.put_to_world(self.world)
            self.wait_until_falls_down(body)
            scores[i] = self.run(body, springs)
            car.destroy(self.world)

        return scores
