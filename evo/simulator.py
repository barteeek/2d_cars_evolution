import Box2D
import numpy as np
import threading
import sys
import pickle

from evo.world_entities import CarBuilder
from evo.world_entities import Terrain


class Simulator:
    def __init__(self, output_dir, vel_iters, pos_iters, route_len, friction, num_workers):
        self.carBuilder = CarBuilder()
        self.terrain = Terrain(route_len, friction)
        self.vel_iters = vel_iters
        self.pos_iters = pos_iters
        self.speed = 30
        self.num_workers = num_workers
        self.dump_dir = output_dir

        with open(self.dump_dir + "/terrain", 'wb') as handle:
            pickle.dump(self.terrain, handle)

        self.worlds = []
        for i in range(num_workers):
            self.worlds += [Box2D.b2World((0, -9.82))]
            self.end_of_route = self.terrain.put_to_world(self.worlds[-1])

    def worker(self, worlds, world_it, car_it, car, scores):
        body, wheels, springs = car.put_to_world(worlds[world_it])
        self.wait_until_falls_down(body, world_it)
        scores[car_it] = self.run(body, springs, world_it)
        self.destroy_car(worlds[world_it], body, wheels)
    
    def get_random_individual(self):
        return self.carBuilder.get_random_car()

    def wait_until_falls_down(self, car_body, world_it):
        init_y = car_body.position[1]
        while True:
            self._run(1, world_it)
            new_y = car_body.position[1]
            if np.abs(init_y - new_y) < 10e-3:
                break

            init_y = new_y

    def _run(self, iters, world_it):
        for i in range(iters):
            for j in range(60):
                self.worlds[world_it].Step(1. / 60., self.vel_iters, self.pos_iters)
                self.worlds[world_it].ClearForces()

    def run(self, body, springs, world_it):
        step = 5
        prev_x = np.inf
        springs[0].motorSpeed = -self.speed

        self._run(step, world_it)
        number_of_iters = step
        while (not (self.end_of_route[0] <= body.position[0] <= self.end_of_route[1])) and \
            np.abs(prev_x - body.position[0]) >= 10e-4:
            self._run(step, world_it)
            prev_x = body.position[0]
            number_of_iters += step

        if self.end_of_route[0] <= body.position[0] <= self.end_of_route[1]:
            return self.end_of_route[0] + 1./number_of_iters
        return body.position[0]

    def get_scores(self, cars):
        scores = np.zeros(len(cars))
        i = 0
        while i < len(cars):
            threads = []
            for j in range(np.min((len(cars) - i, self.num_workers))):
                threads += [threading.Thread(target=self.worker, args=(self.worlds, j, i + j, cars[i + j], scores))]
                threads[-1].start()
            for j in range(np.min((len(cars) - i, self.num_workers))):
                threads[j].join()
            i += self.num_workers
            sys.stdout.write("\rscores computed in %d%%" % int((i*100.)/float(len(cars))))
            sys.stdout.flush()
        sys.stdout.write("\n")
        return scores

    def destroy_car(self, world, body, wheels):
        world.DestroyBody(body)
        for wheel in wheels:
             world.DestroyBody(wheel)
