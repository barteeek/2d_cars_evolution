import Box2D
import numpy as np
import threading
import sys
import pickle

from evo.world_entities import CarBuilder
from evo.world_entities import Terrain


class Simulator:
    def __init__(self, output_dir, terrain, vel_iters, pos_iters, route_len, friction, num_workers):
        self.carBuilder = CarBuilder()
        self.terrain = terrain
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

    def get_end_of_route(self):
        return self.end_of_route

    def worker(self, worlds, world_it, car_it, car, scores, positions):
        body, wheels, springs = car.put_to_world(worlds[world_it])
        self.wait_until_falls_down(body, world_it)
        score, position = self.run(body, springs, world_it)
        scores[car_it] = score
        positions[car_it] = position
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
        step = 1
        prev_x = -np.inf
        if len(springs) > 0:
            springs[0].motorSpeed = -self.speed
        self._run(step, world_it)
        number_of_iters = step
        the_best_x_it = step
        current_it = step
        start_x = body.position.x
        the_best_x = body.position.x
        while (not (self.end_of_route[0] <= body.position.x <= self.end_of_route[1])) and \
            current_it - the_best_x_it <= 10 and current_it <= 1000: #and np.abs(body.position.x - prev_x) >= step * 1e-02 :
            self._run(step, world_it)
            number_of_iters += step
            if body.position.x > the_best_x:
                the_best_x = body.position.x
                the_best_x_it = current_it
            current_it += step
            prev_x = body.position.x

        if np.abs(body.position[0] - start_x) < 10.:
            score = -100.
        else:
            max_num_iters = 1000. * self.end_of_route[0] / 5000.
            score =  1.0*min(self.end_of_route[0], body.position[0]) / self.end_of_route[0] + (max_num_iters - 1.*number_of_iters) / max_num_iters
        return score, body.position[0]

    def get_scores(self, cars):
        scores = np.zeros(len(cars))
        positions = np.zeros(len(cars))
        i = 0
        while i < len(cars):
            threads = []
            for j in range(np.min((len(cars) - i, self.num_workers))):
                threads += [threading.Thread(target=self.worker, args=(self.worlds, j, i + j, cars[i + j], scores, positions))]
                threads[-1].start()
            for j in range(np.min((len(cars) - i, self.num_workers))):
                threads[j].join()
            i += self.num_workers
            sys.stdout.write("\rscores computed in %d%%" % int((i*100.)/float(len(cars))))
            sys.stdout.flush()
        sys.stdout.write("\n")
        return scores, positions

    def destroy_car(self, world, body, wheels):
        world.DestroyBody(body)
        for wheel in wheels:
             world.DestroyBody(wheel)
