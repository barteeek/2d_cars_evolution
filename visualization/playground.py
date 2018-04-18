from evo.world_entities import (Terrain, CarRepresentation, WheelRepresentation)
from .framework import (Framework, Keys)
import numpy as np

class Playground (Framework):
    name = "Car"
    description = "Keys: left = a, brake = s, right = d, hz down = q, hz up = e"
    hz = 4
    zeta = 0.7
    speed = 50
    bridgePlanks = 20
    counter = 0

    def __init__(self):
        super(Playground, self).__init__()

        terrain = Terrain(100)

        # create some terrain
        terrain.put_to_world(self.world)

        self.c = CarRepresentation()
        self.c.construct_car(1., np.array([
            (-1.5, -0.5),
            (1.5, -0.5),
            (1.5, 0.0),
            (0.0, 0.9),
            (-1.15, 0.9),
            (-1.5, 0.2),]),
        [WheelRepresentation([-1., -1], 0., 0.4), WheelRepresentation([1, -1], 0., 0.4)])
        car, wheels, springs = self.c.put_to_world(self.world)

        self.car = car
        self.wheels = wheels
        self.springs = springs

    def Keyboard(self, key):
        if key == Keys.K_a:
            self.springs[0].motorSpeed = self.speed
        elif key == Keys.K_s:
            self.springs[0].motorSpeed = 0
        elif key == Keys.K_d:
            self.springs[0].motorSpeed = -self.speed
        elif key in (Keys.K_q, Keys.K_e):
            if key == Keys.K_q:
                self.hz = max(0, self.hz - 1.0)
            else:
                self.hz += 1.0

            for spring in self.springs:
                spring.springFrequencyHz = self.hz

    def Step(self, settings):
        super(Playground, self).Step(settings)
        self.viewCenter = (self.car.position.x, 20)
        self.Print("frequency = %g hz, damping ratio = %g" %
                   (self.hz, self.zeta))
